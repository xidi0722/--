from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase

# 配置為使用 OpenGL ES
loadPrcFileData('', 'load-display pandagles2')

class TestBase(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.model = self.loader.loadModel("blender/robo1.glb")
        self.model.reparentTo(self.render)
        self.cam.setPos(8, 3, 3)
        self.cam.lookAt(self.model)

        # 檢查手臂節點
        left_arm = self.model.find("**/left_arm")
        right_arm = self.model.find("**/right_arm")
        print("Left arm children:", left_arm.getChildren())
        print("Right arm children:", right_arm.getChildren())
        print("Left arm bounds:", left_arm.getBounds())
        print("Right arm bounds:", right_arm.getBounds())

app = TestBase()
app.run()