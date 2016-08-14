def ebay_category(monkey_category):
    cat_dict = {"Art & Theater Aficionados": "Art",
                "Auto Enthusiasts": "Cars",
                "Avid Investors": "Investment",
                "Beauty Mavens": "Cosmetic",
                "Cooking Enthusiasts": "Cooking",
                "Do-It-Yourselfers": "DIY",
                "Fashionistas": "Fashion",
                "Fast Food Cravers": "Fast Food Crave",
                "Foodies": "Cookbook",
                "Gamers": "Video Games",
                "Green Living Enthusiasts": "Natural",
                "Health & Fitness Buffs": "Fitness",
                "Home Decor Enthusiasts": "Decor",
                "Movie & TV Lovers": "Movie",
                "Music Lovers": "Music",
                "News Junkies & Avid Readers": "Bestseller Book",
                "Nightlife Enthusiasts": "Nightlife",
                "Pet Lovers": "Pet Supplies",
                "Political Junkies": "Political",
                "Savvy Parents": "Savvy Parents",
                "Shoppers": "Home",
                "Shutterbugs": "Cameras",
                "Sport Fans": "Sports",
                "Technophiles": "Electronics",
                "Thrill Seekers": "Sports",
                "Travel Buffs": "Travel"}
    if monkey_category in cat_dict.keys():
        return cat_dict[monkey_category]
    return ""
