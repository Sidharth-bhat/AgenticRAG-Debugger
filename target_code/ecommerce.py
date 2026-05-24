# target_code/ecommerce.py

class ShoppingCart:
    def __init__(self):
        self.items = []
        self.total = 0

    def add_item(self, name, price):
        item = {"name": name, "price": price}
        self.items.append(item)
        # Keep `self.total` accurate via calculate_total()

    def calculate_total(self):
        # Calculate total fresh from items to avoid double-counting
        subtotal = sum(item["price"] for item in self.items)
        self.total = subtotal
        return self.total

    def checkout(self, tax_rate):
        subtotal = self.calculate_total()
        total = subtotal + (subtotal * tax_rate)
        print(f"Total to pay: {total}")
        # Keep `self.total` as the calculated subtotal (pre-tax) to match expectations
        self.total = subtotal