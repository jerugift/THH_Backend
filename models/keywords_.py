from models.sql import job_detail
import json

def extract_keywords_and_save(text, nlp, email, is_file=True):
    if is_file:
        with open(text, encoding='utf-8') as f:
            text = f.read()

    doc = nlp(text)

    output_data = {
        "Job title": "",
        "Must have": [],
        "Good to have": [],
        # "Locations": "",
        "Experiences": "",
    }

    seen_skills = set()
    for ent in doc.ents:
        if ent.text not in seen_skills:
            if ent.label_ == "MUST HAVE":
                output_data["Must have"].append(ent.text)
            elif ent.label_ == "GOOD TO HAVE":
                output_data["Good to have"].append(ent.text)
            # elif ent.label_ == "LOCATION":
            #     output_data["Locations"] = ent.text
            elif ent.label_ == "EXPERIENCE":
                output_data["Experiences"] = ent.text
            elif ent.label_ == "JOB TITLE":
                output_data['Job title'] = ent.text

            seen_skills.add(ent.text)
    final = json.dumps(output_data, indent=4)
    final_load = json.loads(final)

    # Save to database
    job_id=job_detail(text, final_load, email)

    return final,job_id,text