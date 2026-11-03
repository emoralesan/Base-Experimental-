import os, json, csv, argparse, subprocess, sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

SYSTEM='''Eres un evaluador de fidelidad de RAG. Evalúa SOLO si la afirmación está respaldada por el contexto proporcionado, no por conocimiento externo. Responde exclusivamente un objeto JSON con dos campos: label ("Supported" o "Not Supported") y reason (explicación breve en español). Si no hay evidencia suficiente, responde "Not Supported".'''

def main():
    load_dotenv()
    p=argparse.ArgumentParser(); p.add_argument('--input',default='data/processed/sample.jsonl'); p.add_argument('--output',default='results/predictions.csv'); p.add_argument('--skip-reports', action='store_true', help='No generar informes automáticos'); a=p.parse_args()
    client=OpenAI(); model=os.getenv('OPENAI_MODEL','gpt-4.1-mini')
    rows=[]
    for line in Path(a.input).read_text(encoding='utf-8').splitlines():
        r=json.loads(line)
        context=r['context']
        context_text='\n'.join(x.get('text',str(x)) if isinstance(x,dict) else str(x) for x in context) if isinstance(context,list) else str(context)
        user=f"Pregunta: {r['query']}\nContexto:\n{context_text}\nAfirmación a evaluar: {r['sentence']}"
        try:
            response=client.chat.completions.create(model=model,temperature=0,response_format={'type':'json_object'},messages=[{'role':'system','content':SYSTEM},{'role':'user','content':user}])
            raw=response.choices[0].message.content
            parsed=json.loads(raw)
            label=parsed.get('label','')
            if label not in ('Supported','Not Supported'): raise ValueError('Etiqueta no válida')
            reason=parsed.get('reason',''); error=''
        except Exception as e:
            label='';reason='';error=str(e);raw=''
        rows.append({'id':r['id'],'human_label':r['human_label'],'judge_label':label,'reason':reason,'raw_output':raw,'error':error,'model':model,'fine_grained_factuality':r.get('fine_grained_factuality','')})
        print(f"{r['id']}: humano={r['human_label']} juez={label or 'ERROR'}")
    output=Path(a.output);output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    print(f'Resultados guardados en {output}')
    if not a.skip_reports:
        project_root = Path(__file__).resolve().parent.parent
        scripts = Path(__file__).resolve().parent
        commands = [
            [sys.executable, str(scripts / 'evaluate.py'), '--input', str(output.resolve())],
            [sys.executable, str(scripts / 'analyze_errors.py'), '--predictions', str(output.resolve()), '--sample', str(Path(a.input).resolve())],
        ]
        for command in commands:
            print(f'\nEjecutando informe: {Path(command[1]).name}', flush=True)
            subprocess.run(command, cwd=project_root, check=True)
        print('\nExperimento e informes completados. Abre results/error_analysis/report.html')
if __name__=='__main__': main()
