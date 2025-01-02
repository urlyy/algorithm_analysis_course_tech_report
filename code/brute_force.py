import pygame
import random
import math

# 初始化pygame
pygame.init()

# 设置屏幕大小
WIDTH, HEIGHT = 1800, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("多小球碰撞模拟")

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 小球类
class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def update(self):
        self.x += self.vx
        self.y += self.vy

        # 防止小球飞出边界，加入缓冲区域
        if self.x - self.radius < 0:
            self.x = self.radius  # 将小球设置为边界位置
            self.vx = abs(self.vx)  # 反向速度
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius  # 将小球设置为边界位置
            self.vx = -abs(self.vx)  # 反向速度

        if self.y - self.radius < 0:
            self.y = self.radius  # 将小球设置为边界位置
            self.vy = abs(self.vy)  # 反向速度
        elif self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius  # 将小球设置为边界位置
            self.vy = -abs(self.vy)  # 反向速度

    def collide(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.radius + other.radius:
            angle = math.atan2(dy, dx)

            # 计算速度分量
            speed1 = math.sqrt(self.vx**2 + self.vy**2)
            speed2 = math.sqrt(other.vx**2 + other.vy**2)

            direction1 = math.atan2(self.vy, self.vx)
            direction2 = math.atan2(other.vy, other.vx)

            new_vx1 = speed1 * math.cos(direction1 - angle)
            new_vy1 = speed1 * math.sin(direction1 - angle)
            new_vx2 = speed2 * math.cos(direction2 - angle)
            new_vy2 = speed2 * math.sin(direction2 - angle)

            # 交换速度
            final_vx1 = ((self.radius - other.radius) * new_vx1 + (other.radius + other.radius) * new_vx2) / (self.radius + other.radius)
            final_vy1 = new_vy1
            final_vx2 = ((self.radius + self.radius) * new_vx1 + (other.radius - self.radius) * new_vx2) / (self.radius + other.radius)
            final_vy2 = new_vy2

            self.vx = math.cos(angle) * final_vx1 + math.cos(angle + math.pi / 2) * final_vy1
            self.vy = math.sin(angle) * final_vx1 + math.sin(angle + math.pi / 2) * final_vy1
            other.vx = math.cos(angle) * final_vx2 + math.cos(angle + math.pi / 2) * final_vy2
            other.vy = math.sin(angle) * final_vx2 + math.sin(angle + math.pi / 2) * final_vy2

            # 防止小球重叠
            overlap = self.radius + other.radius - distance
            angle_fix = math.atan2(dy, dx)

            self.x += math.cos(angle_fix) * overlap / 2
            self.y += math.sin(angle_fix) * overlap / 2
            other.x -= math.cos(angle_fix) * overlap / 2
            other.y -= math.sin(angle_fix) * overlap / 2

# 创建多个小球
balls = []
num_balls = 100
for _ in range(num_balls):
    radius = random.randint(10, 15)
    x = random.randint(radius, WIDTH - radius)
    y = random.randint(radius, HEIGHT - radius)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    balls.append(Ball(x, y, radius, color))

# 帧率相关变量
clock = pygame.time.Clock()
frame_count = 0
last_time = pygame.time.get_ticks()
fps = 0

# 游戏主循环
running = True
while running:
    screen.fill(WHITE)
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新小球位置并检测碰撞
    for ball in balls:
        ball.update()
        ball.draw()

    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            balls[i].collide(balls[j])

    # 计算并显示帧率
    frame_count += 1
    current_time = pygame.time.get_ticks()
    if current_time - last_time >= 1000:  # 每秒更新一次
        fps = frame_count
        frame_count = 0
        last_time = current_time

    # 显示FPS
    font = pygame.font.SysFont('Arial', 24)
    fps_text = font.render(f"FPS: {fps}", True, BLACK)
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()

    # 控制帧率
    clock.tick()  # 不限制帧率

# 退出游戏
pygame.quit()
