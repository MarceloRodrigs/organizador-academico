
import calendar as calendario_python
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from django.utils import timezone

from .models import Disciplina, Tarefa, Prova, Anotacao, Nota



# INÍCIO

def home(request):
    hoje = timezone.localdate()
    limite = hoje + timedelta(days=7)

    total_disciplinas = Disciplina.objects.count()
    total_tarefas_cadastradas = Tarefa.objects.count()
    total_tarefas = Tarefa.objects.filter(concluida=False).count()
    tarefas_concluidas = Tarefa.objects.filter(concluida=True).count()
    total_provas = Prova.objects.count()

    # Estatísticas das notas
    lista_notas = list(Nota.objects.select_related('disciplina').all())

    total_notas = len(lista_notas)

    soma_pesos = sum(
        (nota.peso for nota in lista_notas),
        Decimal('0')
    )

    soma_ponderada = sum(
        (nota.valor * nota.peso for nota in lista_notas),
        Decimal('0')
    )

    if soma_pesos > 0:
        media_geral = (soma_ponderada / soma_pesos).quantize(
            Decimal('0.01')
        )
    else:
        media_geral = Decimal('0.00')

    # Média ponderada por disciplina
    medias_disciplinas = []

    disciplinas_com_notas = Disciplina.objects.filter(
        notas__isnull=False
    ).distinct()

    for disciplina in disciplinas_com_notas:
        notas_disciplina = disciplina.notas.all()

        peso_total = sum(
            (nota.peso for nota in notas_disciplina),
            Decimal('0')
        )

        if peso_total > 0:
            pontos = sum(
                (
                    nota.valor * nota.peso
                    for nota in notas_disciplina
                ),
                Decimal('0')
            )

            media = (pontos / peso_total).quantize(
                Decimal('0.01')
            )

            medias_disciplinas.append({
                'disciplina': disciplina,
                'media': media
            })

    medias_disciplinas.sort(
        key=lambda item: item['media'],
        reverse=True
    )

    if medias_disciplinas:
        melhor_desempenho = medias_disciplinas[0]
    else:
        melhor_desempenho = None

    if total_tarefas_cadastradas > 0:
        percentual_conclusao = round(
            (tarefas_concluidas / total_tarefas_cadastradas) * 100
        )
    else:
        percentual_conclusao = 0

    tarefas_atrasadas = Tarefa.objects.filter(
        concluida=False,
        data_entrega__lt=hoje
    ).order_by('data_entrega')

    tarefas_proximas = Tarefa.objects.filter(
        concluida=False,
        data_entrega__gte=hoje,
        data_entrega__lte=limite
    ).order_by('data_entrega')

    provas_proximas = Prova.objects.filter(
        data_prova__gte=hoje,
        data_prova__lte=limite
    ).order_by('data_prova')

    return render(request, 'core/home.html', {
        'total_disciplinas': total_disciplinas,
        'total_tarefas': total_tarefas,
        'total_tarefas_cadastradas': total_tarefas_cadastradas,
        'tarefas_concluidas': tarefas_concluidas,
        'total_provas': total_provas,
        'percentual_conclusao': percentual_conclusao,
        'tarefas_atrasadas': tarefas_atrasadas,
        'tarefas_proximas': tarefas_proximas,
        'provas_proximas': provas_proximas,

        # Dados acadêmicos
        'total_notas': total_notas,
        'media_geral': media_geral,
        'medias_disciplinas': medias_disciplinas,
        'melhor_desempenho': melhor_desempenho
    })


# DISCIPLINAS

def disciplinas(request):
    lista_disciplinas = Disciplina.objects.all()

    return render(request, 'core/disciplinas.html', {
        'disciplinas': lista_disciplinas
    })


def cadastrar_disciplina(request):
    if request.method == 'POST':
        Disciplina.objects.create(
            nome=request.POST.get('nome'),
            professor=request.POST.get('professor'),
            codigo=request.POST.get('codigo'),
            semestre=request.POST.get('semestre'),
            descricao=request.POST.get('descricao')
        )

        return redirect('disciplinas')

    return render(request, 'core/cadastrar_disciplina.html')


def editar_disciplina(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)

    if request.method == 'POST':
        disciplina.nome = request.POST.get('nome')
        disciplina.professor = request.POST.get('professor')
        disciplina.codigo = request.POST.get('codigo')
        disciplina.semestre = request.POST.get('semestre')
        disciplina.descricao = request.POST.get('descricao')

        disciplina.save()

        return redirect('disciplinas')

    return render(request, 'core/editar_disciplina.html', {
        'disciplina': disciplina
    })


def excluir_disciplina(request, disciplina_id):
    if request.method == 'POST':
        disciplina = get_object_or_404(Disciplina, id=disciplina_id)
        disciplina.delete()

    return redirect('disciplinas')


# TAREFAS

def tarefas(request):
    status = request.GET.get('status', 'todas')

    lista_tarefas = Tarefa.objects.all()

    if status == 'pendentes':
        lista_tarefas = lista_tarefas.filter(concluida=False)

    elif status == 'concluidas':
        lista_tarefas = lista_tarefas.filter(concluida=True)

    lista_tarefas = lista_tarefas.order_by('data_entrega')

    return render(request, 'core/tarefas.html', {
        'tarefas': lista_tarefas,
        'status_atual': status
    })


def cadastrar_tarefa(request):
    disciplinas_disponiveis = Disciplina.objects.all()

    if request.method == 'POST':
        disciplina_id = request.POST.get('disciplina')
        disciplina = None

        if disciplina_id:
            disciplina = get_object_or_404(Disciplina, id=disciplina_id)

        Tarefa.objects.create(
            titulo=request.POST.get('titulo'),
            descricao=request.POST.get('descricao'),
            disciplina=disciplina,
            data_entrega=request.POST.get('data_entrega') or None
        )

        return redirect('tarefas')

    return render(request, 'core/cadastrar_tarefa.html', {
        'disciplinas': disciplinas_disponiveis
    })


def concluir_tarefa(request, tarefa_id):
    if request.method == 'POST':
        tarefa = get_object_or_404(Tarefa, id=tarefa_id)
        tarefa.concluida = not tarefa.concluida
        tarefa.save()

    return redirect('tarefas')


def excluir_tarefa(request, tarefa_id):
    if request.method == 'POST':
        tarefa = get_object_or_404(Tarefa, id=tarefa_id)
        tarefa.delete()

    return redirect('tarefas')


def editar_tarefa(request, tarefa_id):
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)
    disciplinas_disponiveis = Disciplina.objects.all()

    if request.method == 'POST':
        tarefa.titulo = request.POST.get('titulo')
        tarefa.descricao = request.POST.get('descricao')

        disciplina_id = request.POST.get('disciplina')

        if disciplina_id:
            tarefa.disciplina = get_object_or_404(
                Disciplina,
                id=disciplina_id
            )
        else:
            tarefa.disciplina = None

        tarefa.data_entrega = request.POST.get('data_entrega') or None
        tarefa.save()

        return redirect('tarefas')

    return render(request, 'core/editar_tarefa.html', {
        'tarefa': tarefa,
        'disciplinas': disciplinas_disponiveis
    })


# PROVAS

def provas(request):
    lista_provas = Prova.objects.all().order_by('data_prova')

    return render(request, 'core/provas.html', {
        'provas': lista_provas
    })


def cadastrar_prova(request):
    disciplinas_disponiveis = Disciplina.objects.all()

    if request.method == 'POST':
        disciplina = get_object_or_404(
            Disciplina,
            id=request.POST.get('disciplina')
        )

        Prova.objects.create(
            titulo=request.POST.get('titulo'),
            disciplina=disciplina,
            data_prova=request.POST.get('data_prova'),
            horario=request.POST.get('horario') or None,
            descricao=request.POST.get('descricao')
        )

        return redirect('provas')

    return render(request, 'core/cadastrar_prova.html', {
        'disciplinas': disciplinas_disponiveis
    })


def excluir_prova(request, prova_id):
    if request.method == 'POST':
        prova = get_object_or_404(Prova, id=prova_id)
        prova.delete()

    return redirect('provas')


def editar_prova(request, prova_id):
    prova = get_object_or_404(Prova, id=prova_id)
    disciplinas_disponiveis = Disciplina.objects.all()

    if request.method == 'POST':
        prova.titulo = request.POST.get('titulo')
        prova.disciplina = get_object_or_404(
            Disciplina,
            id=request.POST.get('disciplina')
        )
        prova.data_prova = request.POST.get('data_prova')
        prova.horario = request.POST.get('horario') or None
        prova.descricao = request.POST.get('descricao')

        prova.save()

        return redirect('provas')

    return render(request, 'core/editar_prova.html', {
        'prova': prova,
        'disciplinas': disciplinas_disponiveis
    })


# CALENDÁRIO MENSAL

def calendario(request):
    hoje = timezone.localdate()

    try:
        mes = int(request.GET.get('mes', hoje.month))
        ano = int(request.GET.get('ano', hoje.year))

        if mes < 1 or mes > 12:
            raise ValueError

        if ano < 1900 or ano > 2100:
            raise ValueError

    except (TypeError, ValueError):
        mes = hoje.month
        ano = hoje.year

    primeiro_dia = date(ano, mes, 1)
    ultimo_dia_numero = calendario_python.monthrange(ano, mes)[1]
    ultimo_dia = date(ano, mes, ultimo_dia_numero)

    tarefas = list(
        Tarefa.objects.filter(
            data_entrega__gte=primeiro_dia,
            data_entrega__lte=ultimo_dia
        ).order_by('data_entrega')
    )

    provas = list(
        Prova.objects.filter(
            data_prova__gte=primeiro_dia,
            data_prova__lte=ultimo_dia
        ).order_by('data_prova')
    )

    tarefas_por_data = {}
    provas_por_data = {}

    for tarefa in tarefas:
        tarefas_por_data.setdefault(tarefa.data_entrega, []).append(tarefa)

    for prova in provas:
        provas_por_data.setdefault(prova.data_prova, []).append(prova)

    semanas_numeros = calendario_python.monthcalendar(ano, mes)
    semanas = []

    for semana in semanas_numeros:
        dias = []

        for numero_dia in semana:
            if numero_dia == 0:
                dias.append(None)
            else:
                data_dia = date(ano, mes, numero_dia)

                dias.append({
                    'numero': numero_dia,
                    'data': data_dia,
                    'tarefas': tarefas_por_data.get(data_dia, []),
                    'provas': provas_por_data.get(data_dia, []),
                    'hoje': data_dia == hoje
                })

        semanas.append(dias)

    nomes_meses = [
        '',
        'Janeiro',
        'Fevereiro',
        'Março',
        'Abril',
        'Maio',
        'Junho',
        'Julho',
        'Agosto',
        'Setembro',
        'Outubro',
        'Novembro',
        'Dezembro'
    ]

    mes_anterior = mes - 1
    ano_anterior = ano

    if mes_anterior == 0:
        mes_anterior = 12
        ano_anterior -= 1

    mes_seguinte = mes + 1
    ano_seguinte = ano

    if mes_seguinte == 13:
        mes_seguinte = 1
        ano_seguinte += 1

    return render(request, 'core/calendario.html', {
        'semanas': semanas,
        'mes': mes,
        'ano': ano,
        'nome_mes': nomes_meses[mes],
        'mes_anterior': mes_anterior,
        'ano_anterior': ano_anterior,
        'mes_seguinte': mes_seguinte,
        'ano_seguinte': ano_seguinte,
        'tarefas': tarefas,
        'provas': provas
    })


# ANOTAÇÕES

def anotacoes(request):
    termo = request.GET.get('q', '').strip()

    lista_anotacoes = Anotacao.objects.all()

    if termo:
        lista_anotacoes = lista_anotacoes.filter(
            Q(titulo__icontains=termo) |
            Q(conteudo__icontains=termo)
        )

    lista_anotacoes = lista_anotacoes.order_by('-data_criacao')

    return render(request, 'core/anotacoes.html', {
        'anotacoes': lista_anotacoes,
        'termo': termo
    })


def cadastrar_anotacao(request):
    disciplinas_disponiveis = Disciplina.objects.all()

    if request.method == 'POST':
        disciplina_id = request.POST.get('disciplina')
        disciplina = None

        if disciplina_id:
            disciplina = get_object_or_404(
                Disciplina,
                id=disciplina_id
            )

        Anotacao.objects.create(
            titulo=request.POST.get('titulo'),
            conteudo=request.POST.get('conteudo'),
            disciplina=disciplina
        )

        return redirect('anotacoes')

    return render(request, 'core/cadastrar_anotacao.html', {
        'disciplinas': disciplinas_disponiveis
    })


def editar_anotacao(request, anotacao_id):
    anotacao = get_object_or_404(Anotacao, id=anotacao_id)
    disciplinas_disponiveis = Disciplina.objects.all()

    if request.method == 'POST':
        anotacao.titulo = request.POST.get('titulo')
        anotacao.conteudo = request.POST.get('conteudo')

        disciplina_id = request.POST.get('disciplina')

        if disciplina_id:
            anotacao.disciplina = get_object_or_404(
                Disciplina,
                id=disciplina_id
            )
        else:
            anotacao.disciplina = None

        anotacao.save()

        return redirect('anotacoes')

    return render(request, 'core/editar_anotacao.html', {
        'anotacao': anotacao,
        'disciplinas': disciplinas_disponiveis
    })


def excluir_anotacao(request, anotacao_id):
    if request.method == 'POST':
        anotacao = get_object_or_404(Anotacao, id=anotacao_id)
        anotacao.delete()

    return redirect('anotacoes')


# NOTAS

def notas(request):
    lista_notas = Nota.objects.select_related(
        'disciplina'
    ).all().order_by(
        'disciplina__nome',
        'data_avaliacao'
    )

    disciplinas_com_notas = Disciplina.objects.filter(
        notas__isnull=False
    ).distinct()

    medias = []

    for disciplina in disciplinas_com_notas:
        notas_disciplina = disciplina.notas.all()

        soma_pesos = notas_disciplina.aggregate(
            total=Sum('peso')
        )['total'] or Decimal('0')

        if soma_pesos > 0:
            soma_ponderada = sum(
                (nota.valor * nota.peso for nota in notas_disciplina),
                Decimal('0')
            )

            media = soma_ponderada / soma_pesos
        else:
            media = Decimal('0')

        medias.append({
            'disciplina': disciplina,
            'media': media.quantize(Decimal('0.01'))
        })

    return render(request, 'core/notas.html', {
        'notas': lista_notas,
        'medias': medias,
        'disciplinas': Disciplina.objects.all()
    })


def cadastrar_nota(request):
    disciplinas_disponiveis = Disciplina.objects.all()

    if request.method == 'POST':
        try:
            valor = Decimal(request.POST.get('valor', '').replace(',', '.'))
            peso = Decimal(request.POST.get('peso', '1').replace(',', '.'))

            if valor < 0 or valor > 10:
                raise ValueError

            if peso <= 0:
                raise ValueError

        except (InvalidOperation, ValueError):
            return render(request, 'core/cadastrar_nota.html', {
                'disciplinas': disciplinas_disponiveis,
                'erro': 'Informe uma nota entre 0 e 10 e um peso maior que zero.'
            })

        disciplina = get_object_or_404(
            Disciplina,
            id=request.POST.get('disciplina')
        )

        Nota.objects.create(
            titulo=request.POST.get('titulo'),
            disciplina=disciplina,
            valor=valor,
            peso=peso,
            data_avaliacao=request.POST.get('data_avaliacao') or None,
            descricao=request.POST.get('descricao')
        )

        return redirect('notas')

    return render(request, 'core/cadastrar_nota.html', {
        'disciplinas': disciplinas_disponiveis
    })


def editar_nota(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)
    disciplinas_disponiveis = Disciplina.objects.all()

    if request.method == 'POST':
        try:
            valor = Decimal(request.POST.get('valor', '').replace(',', '.'))
            peso = Decimal(request.POST.get('peso', '1').replace(',', '.'))

            if valor < 0 or valor > 10:
                raise ValueError

            if peso <= 0:
                raise ValueError

        except (InvalidOperation, ValueError):
            return render(request, 'core/editar_nota.html', {
                'nota': nota,
                'disciplinas': disciplinas_disponiveis,
                'erro': 'Informe uma nota entre 0 e 10 e um peso maior que zero.'
            })

        nota.titulo = request.POST.get('titulo')
        nota.disciplina = get_object_or_404(
            Disciplina,
            id=request.POST.get('disciplina')
        )
        nota.valor = valor
        nota.peso = peso
        nota.data_avaliacao = request.POST.get('data_avaliacao') or None
        nota.descricao = request.POST.get('descricao')

        nota.save()

        return redirect('notas')

    return render(request, 'core/editar_nota.html', {
        'nota': nota,
        'disciplinas': disciplinas_disponiveis
    })


def excluir_nota(request, nota_id):
    if request.method == 'POST':
        nota = get_object_or_404(Nota, id=nota_id)
        nota.delete()

    return redirect('notas')
