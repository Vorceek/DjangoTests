import json

# Carrega o arquivo fixture antigo
with open('atividades_old.json', 'r', encoding='utf-16') as f:
    data = json.load(f)

# Exemplo de como modificar cada registro:
for registro in data:
    # Atualize o nome do model:
    registro['model'] = 'atividade_app.registroatividademodel'  # ajuste conforme necessário

    # Atualize os campos:
    # Suponha que o campo antigo "colaborador" agora se chama "RAM_colaborador", etc.
    campos = registro['fields']
    campos['RAM_colaborador'] = campos.pop('colaborador')
    campos['RAM_cliente'] = campos.pop('cliente')
    campos['RAM_servico'] = campos.pop('servico')
    campos['RAM_atividade'] = campos.pop('atividade')
    campos['RAM_dataInicial'] = campos.pop('hora')
    campos['RAM_ativo'] = campos.pop('ativo')
    campos['RAM_dataFinal'] = campos.pop('data_fim')
    # Se houver outros campos que precisam ser renomeados, atualize aqui

# Salva o novo fixture
with open('atividades_new.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
