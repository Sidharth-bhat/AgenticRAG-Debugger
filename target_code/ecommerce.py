# target_code/ecommerce.py

class ShoppingCart:
    def __init__(self):
        self.items = []
        self.total = 0

    def add_item(self, name, price):
        item = {"name": name, "price": price}
        self.items.append(item)
        # BUG: Forgot to update self.total here
    
    def calculate_total(self):
        # BUG: 'item' is a dict, but we try to access it like an object (item.price)
        # It should be item['price']
        for item in self.items:
            self.total += item.price 
        return self.total

    def checkout(self, tax_rate):
        subtotal = self.calculate_total()
        # BUG: tax_rate is expected to be 0.10, but if user passes 10, it breaks logic
        total = subtotal + (subtotal * tax_rate)
        print(f"Total to pay: {total}")