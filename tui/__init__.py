import pytermgui as ptg

CONFIG = """
config:
    InputField:
        styles:
            fill: '[@236]{item}'
            value: '[72]{item}'

    Label:
        styles:
            value: dim bold

    Window:
        styles:
            border: '60'
            corner: '60'

    Container:
        styles:
            border: '96'
            corner: '96'
"""

with ptg.YamlLoader() as loader:
    loader.load(CONFIG)
