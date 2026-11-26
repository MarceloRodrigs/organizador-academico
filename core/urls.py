
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Disciplinas
    path('disciplinas/', views.disciplinas, name='disciplinas'),
    path('disciplinas/cadastrar/', views.cadastrar_disciplina, name='cadastrar_disciplina'),
    path('disciplinas/<int:disciplina_id>/editar/', views.editar_disciplina, name='editar_disciplina'),
    path('disciplinas/<int:disciplina_id>/excluir/', views.excluir_disciplina, name='excluir_disciplina'),

    # Tarefas
    path('tarefas/', views.tarefas, name='tarefas'),
    path('tarefas/cadastrar/', views.cadastrar_tarefa, name='cadastrar_tarefa'),
    path('tarefas/<int:tarefa_id>/concluir/', views.concluir_tarefa, name='concluir_tarefa'),
    path('tarefas/<int:tarefa_id>/excluir/', views.excluir_tarefa, name='excluir_tarefa'),
    path('tarefas/<int:tarefa_id>/editar/', views.editar_tarefa, name='editar_tarefa'),

    # Provas
    path('provas/', views.provas, name='provas'),
    path('provas/cadastrar/', views.cadastrar_prova, name='cadastrar_prova'),
    path('provas/<int:prova_id>/excluir/', views.excluir_prova, name='excluir_prova'),
    path('provas/<int:prova_id>/editar/', views.editar_prova, name='editar_prova'),

    # Calendário
    path('calendario/', views.calendario, name='calendario'),

    # Anotações
    path('anotacoes/', views.anotacoes, name='anotacoes'),
    path('anotacoes/cadastrar/', views.cadastrar_anotacao, name='cadastrar_anotacao'),
    path('anotacoes/<int:anotacao_id>/editar/', views.editar_anotacao, name='editar_anotacao'),
    path('anotacoes/<int:anotacao_id>/excluir/', views.excluir_anotacao, name='excluir_anotacao'),

    # Notas
    path('notas/', views.notas, name='notas'),
    path('notas/cadastrar/', views.cadastrar_nota, name='cadastrar_nota'),
    path('notas/<int:nota_id>/editar/', views.editar_nota, name='editar_nota'),
    path('notas/<int:nota_id>/excluir/', views.excluir_nota, name='excluir_nota'),
]


