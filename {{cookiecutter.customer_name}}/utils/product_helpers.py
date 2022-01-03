def string(value: str) -> str:
    return str(value)

def category_path_helper(value: list) -> list:
    #add required functionality
    return value

def color(value: list) -> list:
    #add required functionality
    return value

def decimal(value: str) -> float:
    try:
        value = float(product[key])
    except ValueError:
        return float(0.00)
    return round(value, 2)

def merging_products(processed_products: list) -> list:
    productIds_list = []
    variant_items = []
    parent_items = []
    final_catalog = []

    #Replace ProductID with Id used to group products, here grouping done based on item_group_id
    for product in processed_products:
        if product["item_group_id"] not in productIds_list:
            productIds_list.append(product["item_group_id"])
            parent_items.append(product)
        else:
            variant_items.append(product)

    for product in parent_items:
        variants = list(filter(lambda p: product['item_group_id'] == p['item_group_id'], variant_items))

        #If catalog needs no variants , but any single variant data say - size must be added in parent product, uncomment below line of code
        '''
        variant_size = [item['size'] for item in variants]
        product["size"] = variant_size
        '''
        #If catalog needs variants, uncomment below line fo code
        '''
        product["variants"] = variant_helper(variants)
        '''

        final_catalog.append(product)
    return final_catalog

# Variant Level Helpers

def variant_helper(variants_list):
    processed_variants = []
    for variant in variants_list:
        unbxd_variant = {}
        for key, value in variant.items():
            unbxd_variant['v_' + key] = value
        unbxd_variant['variantId'] = unbxd_variant.pop('v_uniqueId')
        processed_variants.append(unbxd_variant)
    return processed_variants
