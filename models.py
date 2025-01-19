class Restaurant:
    def __init__(self, id, name, street_address, description):
        self.id = id
        self.name = name
        self.street_address = street_address
        self.description = description 
    def __str__(self):
        return self.name
