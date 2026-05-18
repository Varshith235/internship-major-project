import sqlite3

DB_PATH = 'chat_logs.db'

medical_data = [
    ("What medicine is used for a headache?", "For a headache, over-the-counter pain relievers like Ibuprofen (Advil), Acetaminophen (Tylenol), or Aspirin are commonly used.", "Medical Inquiry"),
    ("Which medicine belongs to malaria?", "Malaria is typically treated with antimalarial drugs such as Chloroquine, Artemether-lumefantrine (Coartem), or Atovaquone-proguanil (Malarone).", "Medical Inquiry"),
    ("What is the treatment for a common cold?", "There is no cure for the common cold, but symptoms can be relieved with rest, hydration, and over-the-counter medicines like decongestants, antihistamines, and pain relievers.", "Medical Inquiry"),
    ("Which medicine is used for diabetes?", "Type 2 diabetes is commonly managed with Metformin, while Type 1 diabetes requires Insulin therapy.", "Medical Inquiry"),
    ("What should I take for a fever?", "Acetaminophen (Tylenol) and Ibuprofen (Advil) are the most common medications used to reduce a fever.", "Medical Inquiry"),
    ("Which medicine belongs to hypertension?", "High blood pressure (hypertension) is often treated with ACE inhibitors (like Lisinopril), Beta-blockers (like Metoprolol), or Calcium channel blockers (like Amlodipine).", "Medical Inquiry"),
    ("What are antibiotics used for?", "Antibiotics like Amoxicillin or Penicillin are used to treat bacterial infections. They do not work against viruses like the common cold or flu.", "Medical Inquiry"),
    ("What is the powerhouse of the cell?", "The mitochondria is known as the powerhouse of the cell because it generates most of the cell's supply of ATP, used as a source of chemical energy.", "Biology Fact"),
    ("What is DNA?", "DNA, or Deoxyribonucleic acid, is the molecule that carries genetic instructions for the development, functioning, growth, and reproduction of all known organisms.", "Biology Fact")
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
for q, a, i in medical_data:
    try:
        cursor.execute('INSERT INTO knowledge_base (question, answer, intent) VALUES (?, ?, ?)', (q, a, i))
    except sqlite3.IntegrityError:
        pass
conn.commit()
conn.close()
print("Medical data seeded!")
