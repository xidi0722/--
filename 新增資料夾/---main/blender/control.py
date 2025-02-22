from panda3d.core import NodePath, PointLight, AmbientLight, loadPrcFile
from panda3d import core
from direct.showbase.ShowBase import ShowBase

loadPrcFile('setting.prc')

class MyApp(ShowBase):
    def __init__(self):
        super().__init__()

        # 載入GLTF模型
        self.model = self.loader.loadModel("robo1.glb")
        
        # 確保模型載入成功
        if self.model.isEmpty():
            print("模型載入失敗")
        else:
            print("模型載入成功")
            self.model.reparentTo(self.render)

        # 列出所有層級的子節點名稱，並確保列出所有骨骼
        print("列出所有層級的子節點名稱：")
        self.print_all_children(self.model)

        # 尋找左右手骨骼
        self.left_arm = self.model.find("**/left_arm")  
        self.right_arm = self.model.find("**/right_arm")  


        # 設定相機位置和朝向
        self.camera.setPos(0, -15, 10)  # 設定相機位置，確保能夠看到模型
        self.camera.lookAt(self.model)    # 設定相機朝向模型

        # 初始化手臂的角度
        self.left_arm_angle = 0
        self.right_arm_angle = 0

        # 添加鍵盤控制
        self.accept("w", self.adjust_arms, [10])  # W 鍵讓雙手上升
        self.accept("s", self.adjust_arms, [-10])  # S 鍵讓雙手下降

        # 添加光源
        self.add_lighting()

    def print_all_children(self, node):
        # 遞迴列印所有子節點名稱
        for child in node.getChildren():
            print(child.getName())  # 輸出每個子節點的名稱
            # 如果該節點還有子節點，遞迴列出
            self.print_all_children(child)

    def rotate_left_arm(self, angle):
        if not self.left_arm.isEmpty():
            # 轉動模型手臂(x,y,z)
            self.left_arm.setHpr(0, 0,angle)  

    def rotate_right_arm(self, angle):
        if not self.right_arm.isEmpty():
            # 轉動模型手臂(x,y,z)
            self.right_arm.setHpr(0,  0,angle) 
            
    def rotate_arms(self, left_angle, right_angle):
        # 控制左右手的角度
        self.rotate_left_arm(left_angle)
        self.rotate_right_arm(right_angle)

    def adjust_arms(self, delta):
        # 調整雙手的角度
        self.left_arm_angle += delta
        self.right_arm_angle += delta
        # 限制角度範圍
        self.left_arm_angle = max(min(self.left_arm_angle, 90), -90)  
        self.right_arm_angle = max(min(self.right_arm_angle, 90), -90)
        self.rotate_arms(self.left_arm_angle, self.right_arm_angle)

    def add_lighting(self):
        # 創建環境光源
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((0.5, 0.5, 0.5, 1))  # 設置輕微的環境光
        ambient_light_node = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_light_node)

        # 創建點光源
        point_light = PointLight('point_light')
        point_light.setColor((1, 1, 1, 1))  # 設置白色光源
        point_light_node = self.render.attachNewNode(point_light)
        point_light_node.setPos(10, -10, 10)  # 設置光源位置
        self.render.setLight(point_light_node)

app = MyApp()
app.run()
