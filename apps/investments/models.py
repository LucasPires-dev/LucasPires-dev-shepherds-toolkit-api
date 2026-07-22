import uuid
from django.db import models


class Investment(models.Model):
    """Investimentos pessoais (reserva financeira e aplicações de prazo)"""

    TYPE_CHOICES = [
        ('cdb', 'CDB'),
        ('lci_lca', 'LCI/LCA'),
        ('tesouro_direto', 'Tesouro Direto'),
        ('poupanca', 'Poupança'),
        ('acoes', 'Ações'),
        ('fiis', 'Fundos Imobiliários'),
        ('fundos', 'Fundos de Investimento'),
        ('criptomoeda', 'Criptomoeda'),
        ('previdencia', 'Previdência Privada'),
        ('outro', 'Outro'),
    ]

    RATE_TYPE_CHOICES = [
        ('prefixado', 'Prefixado (% a.a.)'),
        ('pos_cdi', 'Pós-fixado (% do CDI)'),
        ('pos_ipca', 'IPCA+'),
        ('sem_taxa', 'Sem taxa fixa (renda variável)'),
    ]

    LIQUIDITY_CHOICES = [
        ('daily', 'Liquidez diária'),
        ('at_maturity', 'Somente no vencimento'),
    ]

    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('redeemed', 'Resgatado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='investments')

    name = models.CharField(max_length=150, help_text='Ex: CDB Banco Inter 2026')
    investment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    institution = models.CharField(max_length=100, blank=True, null=True)

    currency = models.CharField(max_length=3, default='BRL', help_text='Código ISO da moeda, ex: BRL, USD')
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True,
                                         help_text='Cotação para BRL na data do aporte (apenas se moeda != BRL)')

    principal_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text='Valor aportado, na moeda do investimento')
    current_value = models.DecimalField(max_digits=12, decimal_places=2, help_text='Valor atual, na moeda do investimento')

    rate_type = models.CharField(max_length=20, choices=RATE_TYPE_CHOICES, default='sem_taxa')
    rate_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                      help_text='Valor da taxa conforme rate_type, ex: 3.65 (% a.a.) ou 100 (% do CDI)')
    fees_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                           help_text='Taxa de administração/custódia, % a.a.')

    start_date = models.DateField()
    maturity_date = models.DateField(null=True, blank=True, help_text='Vazio = sem vencimento definido')
    liquidity = models.CharField(max_length=20, choices=LIQUIDITY_CHOICES,
                                  help_text='Define se este valor conta como reserva financeira')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'investments'
        verbose_name = 'Investimento'
        verbose_name_plural = 'Investimentos'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.get_investment_type_display()}) - {self.currency} {self.current_value}"

    @property
    def counts_as_reserve(self) -> bool:
        return self.status == 'active' and self.liquidity == 'daily'

    @property
    def current_value_brl(self):
        if self.currency == 'BRL' or not self.exchange_rate:
            return self.current_value
        return self.current_value * self.exchange_rate

    @property
    def principal_amount_brl(self):
        if self.currency == 'BRL' or not self.exchange_rate:
            return self.principal_amount
        return self.principal_amount * self.exchange_rate
