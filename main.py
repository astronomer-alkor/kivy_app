from kivy.app import runTouchApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen, ScreenManager

from api_calls import get_catalog, get_product
from categories_structure import CategoriesStructure

screen_manager = ScreenManager()


class ProductScreen(Screen):
    def __init__(self, product, category, product_items, **kwargs):
        super().__init__(**kwargs)
        self.product = product
        self.category = category
        self.product_items = product_items
        Window.bind(on_keyboard=self.prev_screen)

        product_data = get_product(category, product)
        root = Builder.load_file('layouts/product_screen/main.kv')
        root.grid.bind(minimum_height=root.grid.setter('height'))
        root.grid.add_widget(Label(text=product_data['full_name'], height=50, size_hint_y=None))
        head_block = GridLayout(cols=2, size_hint_y=None, height=310, padding=(100, 20))
        image = AsyncImage(
            source=product_data['img_url'], allow_stretch=True, size_hint=(None, None),
        )
        image.size = image.image_ratio * 300, 300
        right_head = GridLayout(rows=2)
        price = Label(
            text=f'{product_data["current_price"]["price_min"]} - {product_data["current_price"]["price_max"]} руб.'
        )
        description = Label(text=product_data['description'])
        head_block.add_widget(image)
        right_head.add_widget(description)
        right_head.add_widget(price)
        head_block.add_widget(right_head)
        root.grid.add_widget(head_block)
        for name, values in product_data['spec'].items():
            root.grid.add_widget(Label(text=name, height=50, size_hint_y=None))
            for key, value in values.items():
                block = GridLayout(rows=1, height=50, size_hint_y=None)
                left = Label(text=key, halign='left')
                block.add_widget(left)
                if isinstance(value, bool):
                    value = 'yes' if value else 'no'
                block.add_widget(Label(text=str(value)))
                root.grid.add_widget(block)

        self.add_widget(root)

    def prev_screen(self, instance, key, *_):
        if key == 27:
            screen_manager.switch_to(
                CatalogScreen(name='catalog', category=self.category, product_items=self.product_items),
                direction='right'
            )
            return True


class ProductItem(ButtonBehavior, RelativeLayout):
    def __init__(self, product, category, product_items, **kwargs):
        super().__init__(**kwargs)
        self.on_press = self.get_product_page
        self.product = product
        self.category = category
        self.product_items = product_items

    def get_product_page(self):
        screen_manager.switch_to(
            ProductScreen(product=self.product, category=self.category, product_items=self.product_items),
            direction='left'
        )


class CatalogScreen(Screen):
    def __init__(self, category, product_items, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.prev_screen)
        self.category = category
        root = Builder.load_file('layouts/catalog_screen/main.kv')
        root.grid.bind(minimum_height=root.grid.setter('height'))
        for product in product_items:
            product_box = ProductItem(
                category=category, product=product['key'], product_items=product_items, height=350, size_hint_y=None
            )

            image = AsyncImage(
                source=product['img_url'], allow_stretch=True, size_hint=(None, None), pos_hint={'top': .8, 'right': .8}
            )
            image.size = image.image_ratio * 200, 200
            product_box.add_widget(image)

            label1 = Label(text=product['full_name'], pos_hint={'right': .75, 'top': 1})
            product_box.add_widget(label1)

            label3 = Label(text=f'от {product["current_price"]["price_min"]} р.', pos_hint={'right': .75, 'top': .9})
            product_box.add_widget(label3)

            root.grid.add_widget(product_box)
        self.add_widget(root)

    def prev_screen(self, instance, key, *_):
        if key == 27:
            screen_manager.switch_to(
                SubcategoryScreen(name='subcategory', category_name=self.category),
                direction='right'
            )
            return True


class ProductButton(Button):
    def __init__(self, category, url=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 120
        self.url = url
        self.on_press = self.get_subcategory_catalog
        self.category = category

    def get_subcategory_catalog(self):
        screen_manager.switch_to(
            CatalogScreen(name='main', category=self.category, product_items=get_catalog(self.url)),
            direction='left'
        )


class SubcategoryScreen(Screen):
    def __init__(self, category_name, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.prev_screen)
        root = Builder.load_file('layouts/subcategory_screen/main.kv')
        root.grid.bind(minimum_height=root.grid.setter('height'))
        category = CategoriesStructure().structure[category_name]
        for subcategory_name, subcategories in category.items():
            root.grid.add_widget(ProductButton(text=subcategory_name, category=category_name, disabled=True))
            for product in subcategories.values():
                root.grid.add_widget(ProductButton(url=product['url'], category=category_name, text=product['name']))
        self.add_widget(root)

    def prev_screen(self, instance, key, *_):
        if key == 27:
            screen_manager.switch_to(MainScreen(name='main'), direction='right')
            return True


class CategoryButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = 220
        self.on_press = self.update_screen

    def update_screen(self):
        screen_manager.switch_to(SubcategoryScreen(category_name=self.text, name='subcategory'), direction='left')


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_content = Builder.load_file('layouts/main_screen/main.kv')
        main_content.grid_layout.bind(minimum_height=main_content.grid_layout.setter('height'))
        for category, _ in CategoriesStructure().structure.items():
            main_content.grid_layout.add_widget(CategoryButton(text=category))
        self.add_widget(main_content)


if __name__ == '__main__':
    import certifi
    import os

    os.environ['SSL_CERT_FILE'] = certifi.where()
    screen_manager.add_widget(MainScreen(name='main'))
    runTouchApp(screen_manager)
