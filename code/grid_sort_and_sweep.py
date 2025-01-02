import pygame
import random
import math

# 初始化pygame
pygame.init()

# 设置屏幕大小
WIDTH, HEIGHT = 1800, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("多小球碰撞模拟 grid_sort_and_sweep")

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRID_COLOR = (200, 200, 200)  # 网格颜色
BALL_COLOR = (0, 0, 255)      # 小球颜色

# 网格大小（每个网格的边长）
GRID_SIZE = 50

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

        # 防止小球飞出边界
        if self.x - self.radius < 0:  # 左边界
            self.x = self.radius  # 将小球位置调整到边界内
            self.vx = -self.vx  # 反转速度
        elif self.x + self.radius > WIDTH:  # 右边界
            self.x = WIDTH - self.radius  # 将小球位置调整到边界内
            self.vx = -self.vx  # 反转速度

        if self.y - self.radius < 0:  # 上边界
            self.y = self.radius  # 将小球位置调整到边界内
            self.vy = -self.vy  # 反转速度
        elif self.y + self.radius > HEIGHT:  # 下边界
            self.y = HEIGHT - self.radius  # 将小球位置调整到边界内
            self.vy = -self.vy  # 反转速度

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
            if overlap > 0:  # 如果小球有重叠
                angle_fix = math.atan2(dy, dx)
                
                # 将小球分开，确保它们不再重叠
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

# 使用字典存储网格
grid = {}

# 将小球放入网格
def assign_to_grid():
    grid.clear()
    for ball in balls:
        grid_x = int(ball.x // GRID_SIZE)
        grid_y = int(ball.y // GRID_SIZE)
        if (grid_x, grid_y) not in grid:
            grid[(grid_x, grid_y)] = []
        grid[(grid_x, grid_y)].append(ball)

# Sort and Sweep 碰撞检测
def sort_and_sweep():
    # 按照 x 坐标排序
    sorted_balls = sorted(balls, key=lambda ball: ball.x)

    # 检查相邻的小球
    for i in range(len(sorted_balls) - 1):
        ball1 = sorted_balls[i]
        for j in range(i + 1, len(sorted_balls)):
            ball2 = sorted_balls[j]
            # 如果第二个小球与第一个小球的 x 轴差距过大，跳出
            if ball2.x - ball1.x > ball1.radius + ball2.radius:
                break
            ball1.collide(ball2)

# 帧率相关变量
clock = pygame.time.Clock()
frame_count = 0
last_time = pygame.time.get_ticks()
fps = 0

# 游戏主循环
running = True
while running:
    screen.fill(WHITE)
    
    # 绘制网格
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新小球位置并检测碰撞
    assign_to_grid()  # 每一帧更新小球在网格中的分布
    sort_and_sweep()  # 使用 Sort and Sweep 方法检测碰撞

    # 绘制小球
    for ball in balls:
        ball.update()
        ball.draw()

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
