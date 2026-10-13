from qfluentwidgets import StyleSheetBase, Theme

from nicestalker import paths


class StyleSheet(StyleSheetBase):

    def path(self, theme=Theme.AUTO):
        return paths.resource_path('stylesheet.qss')
