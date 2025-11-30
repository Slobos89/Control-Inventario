import csv
import random

categorias = [
    "Guantes", "Gasas", "Jeringas", "Mascarillas", "Cintas adhesivas",
    "Antisepticos", "Algodon", "Vendas", "Apositos", "Suturas",
    "Equipos de suero", "Cateteres", "Bolsas de recoleccion", "Termometros"
]

unidades = ["unidad", "caja", "paquete", "bolsa"]

with open("insumos_bodega.csv", "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file, delimiter=";")

    # Encabezados
    writer.writerow(["nombre", "categoria", "unidad", "stock", "stock_minimo"])

    # 100 registros
    for i in range(100):
        categoria = random.choice(categorias)
        nombre = f"{categoria} {random.randint(1, 5)}"
        unidad = random.choice(unidades)
        stock = random.randint(0, 500)
        stock_minimo = random.randint(10, 100)

        writer.writerow([nombre, categoria, unidad, stock, stock_minimo])

print("CSV generado correctamente: insumos_bodega.csv")