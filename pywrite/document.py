
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List, Dict, Tuple, Sequence

ja = 392
en = 840

class NodeType(Enum):
    UNKNOWN = 0
    DOCUMENT = 1
    FRONTMATTER = 2
    BACKMATTER = 3
    PART = 4
    CHAPTER = 5

DEFAULT_CONFIG = PywriteConfiguration()

class PywriteConfiguration(object):
    def __init__(self, part_based=False):
        self.part_based = part_based

class PywriteNode(metaclass=ABCMeta):
    def __init__(self, parent: PywriteNode):
        self.parent = parent
    
    @abstractmethod
    def get_type(self) -> NodeType:
        pass

    def get_config(self) -> PywriteConfiguration:
        config = DEFAULT_CONFIG
        if self.hasattr('configuration'):
            config = self.configuration
        elif self.parent is None:
            config = DEFAULT_CONFIG
        else:
            config = self.parent.get_config()
        return config

class Document(PywriteNode):
    def __init__(self, configuration: PywriteConfiguration):
        self.configuration = configuration
        self.frontmatter: Frontmatter = Frontmatter()
        self.child_nodes: List[PywriteNode] = []
        self.backmatter: Backmatter = Backmatter()

    def part(self, title, *args, **kwargs):
        instance = Chapter(title, *args, *kwargs)
        self.add(instance)
        return instance

    def chapter(self, title, *args, **kwargs):
        instance = Chapter(title, *args, *kwargs)
        self.add(instance)
        return instance

    def add(self, node: PywriteNode):
        node_type = node.get_type()
        if self.configuration.part_based:
            if node.__class__ in [Part, Appendices]:
                self.child_nodes.append(node)
            else:
                raise Exception('Not allowed')
        else:
            if node.__class__ in [Chapter, Appendix]:
                self.child_nodes.append(node)
            else:
                raise Exception('Not allowed')

class GroupingNode(PywriteNode, metaclass=ABCMeta):
    def __init__(self, allowable_child_types = []):
        self.child_nodes = []

    def add(self, node: PywriteNode):
        if node.__class__ in self.allowable_child_types:
            self.child_nodes.append(node)
        else:
            raise Exception('Not allowed')

    def concept(self, title, *args, **kwargs):
        instance = Concept(title, *args, *kwargs)
        self.add(instance)
        return instance

    def task(self, title, *args, **kwargs):
        instance = Task(title, *args, *kwargs)
        self.add(instance)
        return instance

    def reference(self, title, *args, **kwargs):
        instance = Reference(title, *args, *kwargs)
        self.add(instance)
        return instance

class SubmapNode(GroupingNode, metaclass=ABCMeta):
    def __init__(self, allowable_child_types = [], leading_topic = None):
        super().__init__(self, allowable_child_types)
        self.leading_topic = leading_topic

class Frontmatter(GroupingNode):
    def __init__(self):
        super().__init__(self, allowable_child_types=[Concept, Reference])

class Part(SubmapNode):
    def __init__(self, title, *kwargs):
        self.title = title

class Chapter(SubmapNode):
    def __init__(self, *args, **kwargs):
        super().__init__(self, [Concept, Task, Reference])
        self.title = ParallelText(*args, *kwargs)

    def en(self, text: str, *args, **kwargs):
        self.title.en(text, *args, *kwargs)
        return self

    def ja(self, text: str, *args, **kwargs):
        self.title.ja(text, *args, *kwargs)
        return self


class Backmatter(GroupingNode):
    def __init__(self):
        super().__init__(self, allowable_child_types=[Concept, Reference])

class Appendices(GroupingNode):
    def __init__(self):
        super().__init__(self, allowable_child_types=[Appendix])

class Topic(GroupingNode):
    def __init__(self, title, *args, **kwargs):
        self.title = title
        self.child_nodes = []
    
    def p(self, texts:[{int, str}]):
        for text in texts:
            print(text)

class Concept(Topic):
    def __init__(self, title, *args, **kwargs):
        super().__init__(title, *args, *kwargs)
        self.title = {}

    def en(self, text: str, *args, **kwargs):
        self.title[en] = Text(text, *args, *kwargs)
        return self

    def ja(self, text: str, *args, **kwargs):
        self.title[ja] = Text(text, *args, *kwargs)
        return self



class Task(Topic):
    pass

class Reference(Topic):
    pass

class Appendix(Topic):
    pass

class Paragraph(PywriteNode):
    def __init__(self, *args, **kwargs):
        self.parallel_texts = []

    def text(self, *args, **kwargs):
        text = ParallelText(self, *args, *kwargs)
        self.parallel_texts.append(text)
        return text

class Note(PywriteNode):
    pass

class Table(PywriteNode):
    pass

class Tree(PywriteNode):
    pass

class Figure(PywriteNode):
    pass

class ParallelText(PywriteNode):
    def __init__(self, *args, **kwargs):
        self.parallel = {}

    def en(self, text: str, *args, **kwargs):
        self.parallel[en] = Text(en, text, *args, *kwargs)
        return self

    def ja(self, text: str, *args, **kwargs):
        self.parallel[ja] = Text(ja, text, *args, *kwargs)
        return self

    def add(self, *texts: [Text]):
        for text in texts:
            self.parallel[text.language] = text

class Text(PywriteNode):
    def __init__(self, language: int, text: str, *args, **kwargs):
        self.language = language
        self.text = text
        self.modifiers = []
        for arg in args:
            if isinstance(arg, Modifier):
                self.modifiers.append(arg)

def text_ja(text: str, *args, **kwargs):
    return Text(ja, text, *args, *kwargs)

def text_en(text: str, *args, **kwargs):
    return Text(en, text, *args, *kwargs)

class Modifier(metaclass=ABCMeta):
    pass


class WinTitle(Modifier):
    def __init__(self, text: str, index: int = 0):
        self.text = text
        self.index = index

class MenuCascade(Modifier):
    def __init__(self, text: str, index: int = 0):
        self.text = text
        self.index = index

class UIControl(Modifier):
    def __init__(self, text: str, index: int = 0):
        self.text = text
        self.index = index

class Superscript(Modifier):
    def __init__(self, text: str, index: int = 0):
        self.text = text
        self.index = index

class Subscript(Modifier):
    def __init__(self, text: str, index: int = 0):
        self.text = text
        self.index = index

class Meta(object):
    pass

class Product(Meta):
    def __init__(self, *applicable_products: [str], exclude=False):
        self.applicable_products = applicable_products
        self.exclude = exclude

if __name__ == '__main__':
    config = PywriteConfiguration()
    document = Document(config)

    ch1 = document.chapter(id='manual.overview').ja('概要').en('Overview')

    con = ch1.concept().ja('セットアップ方法').en('How to set up')

    with con.paragraph() as p:
        p.text().ja('メインウィンドウは、ヘッダー、メインパネルとサイドバーで構成されています。', WinTitle('メイン')
            ).en('The main window consists of a header, a main panel, and a side bar.', WinTitle('main'))
        p.text(Product('PW-003B')).ja('右上のハンバーガーアイコンをクリックして、メニューを開きます。'
            ).en('Open the menu by clicking the humberger icon on the top right corner.')
        p.text().ja('V2バルブを反時計回りに回し、チャンバーにN2を充填します。', Subscript('2', 1)
            ).en('Fill the chamber with N2 by turning the V2 valve counterclockwise.', Subscript('2'))

    with con.paragraph() as p:
        p.text(
            Text(ja, 'V2バルブを反時計回りに回し、チャンバーにN2を充填します。', Subscript('2', 1)), 
            Text(en, 'Fill the chamber with N2 by turning the V2 valve counterclockwise.', Subscript('2'))
        )

    with con.paragraph() as p:
        p.text().add(
            text_ja('V2バルブを反時計回りに回し、チャンバーにN2を充填します。', Subscript('2', 1)), 
            text_en('Fill the chamber with N2 by turning the V2 valve counterclockwise.', Subscript('2'))
        )

    with con.paragraph() as p:
        p.text()
            .ja('複数の分からなる段落にしたい。文章が複数含まれていても一応問題ないものとする。')
            .en(['I would like this paragraph to contain two or more sentences.', 'It is no problem even if two or more sentences are included in this text.'])
