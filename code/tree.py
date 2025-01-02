import pygame
import random
import math

# 初始化pygame
pygame.init()

# 设置屏幕大小
WIDTH, HEIGHT = 1800, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("多小球碰撞模拟 - 四叉树")

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

# 四叉树类
class Quadtree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary  # 四叉树的边界 (矩形区域)
        self.capacity = capacity  # 四叉树节点的容量
        self.balls = []  # 当前节点存储的小球
        self.divided = False  # 是否已经分割

    def subdivide(self):
        x, y, w, h = self.boundary
        half_w = w / 2
        half_h = h / 2

        # 创建四个子区域
        self.nw = Quadtree((x, y, half_w, half_h), self.capacity)  # 西北
        self.ne = Quadtree((x + half_w, y, half_w, half_h), self.capacity)  # 东北
        self.sw = Quadtree((x, y + half_h, half_w, half_h), self.capacity)  # 西南
        self.se = Quadtree((x + half_w, y + half_h, half_w, half_h), self.capacity)  # 东南

        self.divided = True

    def insert(self, ball):
        # 如果小球不在当前区域内，返回False
        if not self.contains(ball):
            return False

        # 如果当前节点可以容纳小球，直接插入
        if len(self.balls) < self.capacity:
            self.balls.append(ball)
            return True
        else:
            # 否则，如果节点已满，分割区域并插入
            if not self.divided:
                self.subdivide()

            # 尝试插入到子节点
            return (self.nw.insert(ball) or
                    self.ne.insert(ball) or
                    self.sw.insert(ball) or
                    self.se.insert(ball))

    def contains(self, ball):
        x, y, w, h = self.boundary
        return (x <= ball.x - ball.radius < x + w and
                y <= ball.y - ball.radius < y + h)

    def query(self, range):
        # 获取范围内的小球
        found = []
        x, y, w, h = range
        if not self.intersects(range):
            return found

        # 检查当前节点的小球
        for ball in self.balls:
            if (range[0] <= ball.x <= range[0] + range[2] and
                range[1] <= ball.y <= range[1] + range[3]):
                found.append(ball)

        # 检查子节点
        if self.divided:
            found.extend(self.nw.query(range))
            found.extend(self.ne.query(range))
            found.extend(self.sw.query(range))
            found.extend(self.se.query(range))

        return found

    def intersects(self, range):
        x, y, w, h = self.boundary
        rx, ry, rw, rh = range
        return not (rx > x + w or rx + rw < x or ry > y + h or ry + rh < y)

# 创建多个小球
balls = []
num_balls = 100
for _ in range(num_balls):
    radius = random.randint(10, 15)  # 小球的半径随机在10到50之间
    x = random.randint(radius, WIDTH - radius)
    y = random.randint(radius, HEIGHT - radius)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    balls.append(Ball(x, y, radius, color))

# 创建四叉树
boundary = (0, 0, WIDTH, HEIGHT)
quadtree = Quadtree(boundary, 4)

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

    # 清空四叉树并将小球添加到四叉树
    quadtree = Quadtree(boundary, 4)  # 重新创建一个新的四叉树
    for ball in balls:
        quadtree.insert(ball)

    # 更新小球位置并检测碰撞
    for ball in balls:
        ball.update()
        ball.draw()

        # 查询周围的球并进行碰撞检测
        nearby_balls = quadtree.query((ball.x - 50, ball.y - 50, 100, 100))
        for other in nearby_balls:
            if ball != other:
                ball.collide(other)

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
