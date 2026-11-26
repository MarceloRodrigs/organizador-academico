
from django.db import models


class Disciplina(models.Model):
    nome = models.CharField(max_length=150)
    professor = models.CharField(max_length=150)
    codigo = models.CharField(max_length=30)
    semestre = models.CharField(max_length=30)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Tarefa(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    data_entrega = models.DateField(null=True, blank=True)
    concluida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class Prova(models.Model):
    titulo = models.CharField(max_length=200)

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE
    )

    data_prova = models.DateField()
    horario = models.TimeField(null=True, blank=True)
    descricao = models.TextField(blank=True)

    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class Anotacao(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class Nota(models.Model):
    titulo = models.CharField(max_length=200)

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name='notas'
    )

    valor = models.DecimalField(max_digits=4, decimal_places=2)

    peso = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.00
    )

    data_avaliacao = models.DateField(null=True, blank=True)

    descricao = models.TextField(blank=True)

    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} - {self.valor}'
