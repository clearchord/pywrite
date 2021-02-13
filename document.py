from enum import IntEnum, Enum
from typing import List

class Lang(IntEnum):
    __ = 0
    ja = 1
    en = 2

class Annotation:
    def __init__(self, type: str, text: str, order: int, prefix: str ='', postfix: str ='') -> None:
        self.type = type # wintitle, uicontrol, sup, sub, footnote
        self.text = text
        self.order = order
        self.prefix = prefix
        self.postfix = postfix

class Footnote(Annotation):
    def __init__(self, text: str, order: int, prefix: str ='', postfix: str ='') -> None:
        super().__init__('footnote', text, order, prefix=prefix, postfix=postfix)

class Text:
    def __init__(self, text: str, annotations: List[Annotation]=[]) -> None:
        self.text = text
        self.annotations = annotations

class Component:
    def __init__(self) -> None:
        pass

class MultilingualText(Component):
    def __init__(self) -> None:
        super().__init__()
        self.body = {}

    def ja(self, text: str, annotations=[]):
        self.body[Lang.ja] = Text(text, annotations=annotations)
        return self

    def en(self, text: str, annotations=[]):
        self.body[Lang.en] = Text(text, annotations=annotations)
        return self

    def __getitem__(self, lang: Lang):
        return self.body[lang]

class Metadata:
    def __init__(self) -> None:
        self.debug = True
    
    def set_author(self, author: MultilingualText):
        self.author = author

class Paragraph(Component):
    def __init__(self) -> None:
        super().__init__()
        self.sentences: List[MultilingualText] = []
    
    def add(self, texts: List[MultilingualText]):
        self.sentences.extend(texts)

class Figure(Component):
    def __init__(self, title: MultilingualText, path_image) -> None:
        super().__init__()
        self.title = title
        self.path_image = path_image

class ContentType(Enum):
    Concept = "concept"
    Task = "task"
    Reference = "reference"

class Content:
    def __init__(self, type: ContentType) -> None:
        self.type = type
        self.components: List[Component] = []

    def add(self, components: List[Component]):
        self.components.extend(components)

class TOC:
    def __init__(self, title: MultilingualText, content: Content = None) -> None:
        self.title = title
        self.content = content
        self.child_nodes = []

    def add(self, child_node: 'TOC') -> 'TOC':
        self.child_nodes.append(child_node)
        return self

    def show(self, lang: Lang, indent: str) -> str:
        text = indent + self.title[lang].text + '\n'
        for child_node in self.child_nodes:
            text += child_node.show(lang, indent + '  ')
        return text

class Document:
    def __init__(self, title: MultilingualText = None):
        self.root = TOC(title)
        self.metadata = None
    
    def getroot(self):
        return self.root

    def add_metadata(self, metadata: Metadata) -> 'Document':
        self.metadata = metadata
        return self

    def show_table_of_contents(self, lang: Lang, indent: str = ''):
        text = self.root.show(lang, indent)
        print(text)

def test():
    title = MultilingualText().ja('Pywrite 入門').en('An Introduction to Pywrite')
    document = Document(title)
    root = document.getroot()
    node = TOC(MultilingualText().ja('概要').en('Overview'))
    root.add(node)
    node = TOC(MultilingualText().ja('はじめに').en('Preface'))
    root.add(node)

    document.show_table_of_contents(Lang.ja)
    document.show_table_of_contents(Lang.en)

if __name__ == '__main__':
    test()

