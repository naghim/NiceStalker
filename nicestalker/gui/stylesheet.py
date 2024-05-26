
from qfluentwidgets import StyleSheetBase, Theme

class StyleSheet(StyleSheetBase):

    def path(self, theme=Theme.AUTO):
        return f"resources/stylesheet.qss"
