import csv

# Lista de insumos de farmacia
insumos = [
    ("Paracetamol 500mg", 200, "2026-05-10"),
    ("Ibuprofeno 400mg", 180, "2026-03-15"),
    ("Amoxicilina 500mg", 120, "2025-11-20"),
    ("Omeprazol 20mg", 150, "2027-01-12"),
    ("Metformina 850mg", 130, "2026-09-08"),
    ("Insulina NPH", 75, "2025-07-30"),
    ("Insulina Rápida", 60, "2025-06-28"),
    ("Salbutamol Inhalador", 90, "2026-04-22"),
    ("Dipirona 500mg", 160, "2026-02-18"),
    ("Tramadol 50mg", 110, "2025-12-14"),
    ("Ondansetron 4mg", 85, "2026-01-05"),
    ("Diclofenaco 50mg", 140, "2026-08-17"),
    ("Prednisona 5mg", 100, "2027-03-03"),
    ("Clorfenamina 4mg", 190, "2026-11-09"),
    ("Losartan 50mg", 175, "2026-10-25"),
    ("Enalapril 10mg", 160, "2027-04-08"),
    ("Aspirina 100mg", 210, "2027-06-15"),
    ("Atorvastatina 20mg", 130, "2026-07-21"),
    ("Metoprolol 50mg", 115, "2026-05-12"),
    ("Sertralina 50mg", 90, "2026-12-02"),
    ("Ketorolaco 10mg", 140, "2025-12-30"),
    ("Ranitidina 150mg", 70, "2026-03-18"),
    ("Loratadina 10mg", 160, "2027-02-09"),
    ("Levofloxacino 500mg", 55, "2025-10-14"),
    ("Ceftriaxona 1g", 90, "2026-01-20"),
    ("Ciprofloxacino 500mg", 130, "2026-11-11"),
    ("Furosemida 40mg", 85, "2025-09-05"),
    ("Omeprazol Inyectable", 60, "2026-06-17"),
    ("Metamizol Inyectable", 90, "2026-03-29"),
    ("Diazepam 10mg", 50, "2027-01-14"),
    ("Clonazepam 2mg", 45, "2026-12-06"),
    ("Jarabe Ambroxol", 70, "2026-04-08"),
    ("Jarabe Paracetamol Pediátrico", 80, "2026-05-19"),
    ("Solución Fisiológica 100ml", 150, "2027-02-17"),
    ("Solución Glucosada 5%", 140, "2026-08-10"),
    ("Gel Antiséptico", 130, "2027-01-27"),
    ("Apósito Estéril 10x10", 200, "2028-03-01"),
    ("Jeringa 3ml", 500, "2029-12-31"),
    ("Jeringa 5ml", 480, "2029-12-31"),
    ("Guantes Estériles Talla M", 220, "2028-07-18"),
    ("Guantes Estériles Talla S", 200, "2028-07-18"),
    ("Mascarilla Quirúrgica", 1000, "2030-01-01"),
    ("Tiritas Adhesivas", 140, "2028-05-21"),
    ("Vaselina Estéril", 60, "2027-09-09"),
    ("Solución Oftálmica Lubricante", 45, "2026-04-11"),
    ("Sutura Seda 2/0", 70, "2029-08-22"),
    ("Sutura Nylon 3/0", 65, "2029-08-22"),
]

# Nombre del archivo a generar
archivo = "farmacia_inventario.csv"

# Crear archivo CSV separado con ;
with open(archivo, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=";")
    
    # Encabezados
    writer.writerow(["Nombre", "Stock", "Vencimiento"])
    
    # Datos
    for item in insumos:
        writer.writerow(item)

print(f"Archivo CSV generado correctamente: {archivo}")