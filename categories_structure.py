from api_calls import get_categories_structure


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CategoriesStructure(metaclass=Singleton):
    def __init__(self):
        self.structure = get_categories_structure()

    def update(self):
        self.structure = get_categories_structure()
