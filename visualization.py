# visualization.py

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from robot_and_initial_state import Robot

class Visualizer:
    def __init__(self, warehouse_matrix: np.ndarray, robots: List['Robot']):
        """
        Visualizer 初始化
        
        :param warehouse_matrix: 2D numpy array (0=aisle, 1=shelf, 2=picking, 3=charge)
        :param robots: Robot 物件的列表。
                       Robot 需有 .position, .charging_status, .battery_level, .charging_threshold 屬性。
        """
        self.matrix = warehouse_matrix
        self.robots = robots
        self.fig, self.ax = plt.subplots(figsize=(12, 10))

        # 統一定義顏色，方便管理
        self.colors = {
            1: '#A5A5A5',            # 貨架 (shelf)
            2: '#FF9800',            # 撿貨站 (picking)
            3: '#2196F3',            # 充電站 (charge)
            4: '#ADD8E6',            # 充電排隊區 (charge queue)
            5: '#00008B',            # 充電出口 (charge exit)
            6: '#FFFACD',            # 撿貨排隊區 (picking queue)
            7: '#FFA500',            # 撿貨出口 (picking exit)
            'working': 'green',      # 工作中
            'low_battery': 'yellow', # 低電量
            'charging': 'red',       # 充電中 (機器人顏色)
            'laden_indicator': '#39FF14' # 搬貨指示器顏色 (亮綠色)
        }

    def _draw_static_background(self):
        """繪製不會變動的倉儲背景 (只在需要時呼叫)。"""
        rows, cols = self.matrix.shape

        # 設定座標軸和網格，Y軸反轉以匹配陣列索引
        self.ax.set_xlim(-0.5, cols - 0.5)
        self.ax.set_ylim(rows - 0.5, -0.5) # Invert y-axis
        self.ax.set_xticks(np.arange(cols + 1) - 0.5, minor=True)
        self.ax.set_yticks(np.arange(rows + 1) - 0.5, minor=True)
        self.ax.grid(which="minor", color="lightgray", linestyle='-', linewidth=0.5)

        # 繪製倉儲背景 (貨架, 撿貨站, 充電站)
        for r in range(rows):
            for c in range(cols):
                cell_type = self.matrix[r, c]
                if cell_type in self.colors:
                    rect = patches.Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor=self.colors[cell_type])
                    self.ax.add_patch(rect)

    def _draw_dynamic_elements(self, sim_time: int):
        """
        繪製會變動的元素 (機器人) 並更新標題。
        """
        for robot in self.robots:
            row, col = robot.position
            
            if robot.charging_status:
                color = self.colors['charging']      # 紅色：充電中
            elif robot.battery_level <= robot.charging_threshold:
                color = self.colors['low_battery']   # 黃色：低電量
            else:
                color = self.colors['working']       # 綠色：工作中

            # 繪製代表機器人的主圓圈
            circ = patches.Circle((col, row), 0.35, facecolor=color, edgecolor='black', zorder=10)
            self.ax.add_patch(circ)

            # 如果機器人正在搬貨，在中間加上一個小方塊
            if robot.carrying_item:
                square_size = 0.25
                # 計算方塊的左下角座標，使其置中
                square_x = col - square_size / 2
                square_y = row - square_size / 2
                laden_indicator = patches.Rectangle(
                    (square_x, square_y), square_size, square_size, 
                    facecolor=self.colors['laden_indicator'], 
                    edgecolor='white',
                    linewidth=0.5,
                    zorder=10.5 # 確保在圓圈之上，文字之下
                )
                self.ax.add_patch(laden_indicator)

            # 繪製機器人 ID 文字
            self.ax.text(col, row, robot.id, ha='center', va='center', color='black', fontsize=8, weight='bold', zorder=11)

        self.ax.set_title(f"Warehouse Simulation - Time: {sim_time}", fontsize=16)

    def draw(self, sim_time: int = 0):
        """
        繪製或更新倉儲的單一影格 (frame)。
        在模擬迴圈中重複呼叫此方法，以產生動態視覺化。
        """
        self.ax.clear()
        self._draw_static_background()
        self._draw_dynamic_elements(sim_time)
        self.ax.set_title(f"Warehouse Simulation - Time: {sim_time}", fontsize=16)
        plt.pause(0.1)  # 暫停讓畫面刷新，這是產生動態效果的關鍵

    def show(self):
        """在模擬結束後，呼叫此方法以保持最終視窗開啟。"""
        plt.show()
