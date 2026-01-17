import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker('ru_RU')

def get_dataset(rows=100):
    np.random.seed(42)
    start_date = datetime(2025, 1, 1)
    
    order_ids = [f"ORD_{i:06d}" for i in range(rows)] + ['ORD_000123'] * (rows//10)
    order_ids = order_ids[:rows]
    
    data = {
        'order_id': order_ids,
        'customer_id': [fake.uuid4() for _ in range(rows)],
        'customer_name': [fake.name() for _ in range(rows)],
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Books', '', None], rows).tolist(),
        'product_name': [fake.word() for _ in range(rows)],
        'quantity': np.random.randint(-5, 20, rows),
        'unit_price': np.random.uniform(-100, 1000, rows),
        'status': np.random.choice(['new', 'processed', 'shipped', 'INVALID', None], rows)
    }
    
    order_dates = [start_date + timedelta(days=random.randint(0, 365)) for _ in range(rows)]
    delivery_dates = []
    for i, order_date in enumerate(order_dates):
        if random.random() < 0.2:  # 20% ошибок
            delivery_dates.append(order_date - timedelta(days=random.randint(1, 30)))
        else:
            delivery_dates.append(order_date + timedelta(days=random.randint(1, 60)))
    
    data['order_date'] = order_dates
    data['delivery_date'] = delivery_dates
    
    data['total_amount'] = []
    for i in range(rows):
        q = data['quantity'][i]
        p = data['unit_price'][i]
        if q > 0 and p > 0:
            data['total_amount'].append(q * p * random.uniform(0.1, 3))
        else:
            data['total_amount'].append(-999)
    
    df = pd.DataFrame(data)
    
    mask = np.random.random(rows) < 0.05
    df.loc[mask, ['customer_id', 'order_date']] = None
    
    print(f"Сгенерировано {len(df)} строк с аномалиями")
    print(f"Отрицательных цен: {(df['unit_price'] < 0).sum()}")
    print(f"NULL значений: {df.isnull().sum().sum()}")
    return df
