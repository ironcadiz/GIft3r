class EbayItem:
    def __init__(self, title, itemUrl, photoUrl, value):
        self.title = title
        self.itemUrl = itemUrl
        self.photoUrl = photoUrl
        self.value = value

    def __str__(self):
        return "{}: CLP${}\n{}".format(self.title, self.value, self.itemUrl)

    def __eq__(self, other):
        return self.title == other.title

    def __hash__(self):
        return hash(('title', self.title))
