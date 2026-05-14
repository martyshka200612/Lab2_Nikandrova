PRAGMA foreign_keys = ON;

CREATE TABLE asset_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL,
    description TEXT NOT NULL,
    uniqueness_type TEXT NOT NULL,
    detail_level INTEGER NOT NULL,
    average_file_size DECIMAL(10,2) NOT NULL
);

CREATE TABLE game_assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_name TEXT NOT NULL,
    source_project TEXT NOT NULL,
    creation_date DATE NOT NULL,
    polygon_count INTEGER NOT NULL,
    material_count INTEGER NOT NULL,
    production_hours INTEGER NOT NULL,
    asset_price DECIMAL(10,2) NOT NULL,
    category_id INTEGER NOT NULL,

    FOREIGN KEY (category_id)
        REFERENCES asset_categories(category_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

INSERT INTO asset_categories
(category_name, description, uniqueness_type, detail_level, average_file_size)
VALUES
('Окружение / props', 'Объекты окружения: бочки, костры, дома, ящики и декоративные элементы', 'переиспользуемый', 2, 120.50),
('Транспорт', 'Транспортные ассеты: машины, мотоциклы, лодки и другие средства передвижения', 'переиспользуемый', 3, 300.75),
('Персонажи', 'Игровые персонажи, NPC и уникальные герои', 'уникальный', 3, 250.50),
('Оружие', 'Категория для оружия и боевого снаряжения', 'переиспользуемый', 2, 85.75),
('Растения', 'Категория для деревьев, кустов и травы', 'переиспользуемый', 1, 35.20);

INSERT INTO game_assets
(asset_name, source_project, creation_date, polygon_count, material_count, production_hours, asset_price, category_id)
VALUES
('Wooden_Barrel_01', 'Fantasy Quest', '2026-02-10', 3200, 2, 6, 45.00,
 (SELECT category_id FROM asset_categories WHERE category_name = 'Окружение / props')),

('CyberBike_X9', 'Neon Protocol', '2026-02-15', 38000, 7, 55, 950.00,
 (SELECT category_id FROM asset_categories WHERE category_name = 'Транспорт')),

('CityCar_Sedan_01', 'Neon Protocol', '2026-02-18', 12000, 4, 14, 160.00,
 (SELECT category_id FROM asset_categories WHERE category_name = 'Транспорт')),

('Skargid_FinalBoss', 'Fantasy Quest', '2026-03-01', 98000, 12, 120, 2400.00,
 (SELECT category_id FROM asset_categories WHERE category_name = 'Персонажи')),

('Village_NPC_Blacksmith', 'Fantasy Quest', '2026-03-04', 32000, 5, 28, 350.00,
 (SELECT category_id FROM asset_categories WHERE category_name = 'Персонажи')),

('Sword_Iron_01', 'Fantasy Quest', '2026-03-05', 8500, 3, 12, 120.00,
 (SELECT category_id FROM asset_categories WHERE category_name = 'Оружие')),

('PineTree_01', 'Forest Survival', '2026-03-08', 6200, 2, 8, 75.50,
 (SELECT category_id FROM asset_categories WHERE category_name = 'Растения'));