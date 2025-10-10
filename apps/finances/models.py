import uuid
from django.db import models


class Finance(models.Model):
    """Gestão financeira"""

    TYPE_CHOICES = [
        ('income', 'Entrada'),
        ('expense', 'Saída'),
    ]

    CATEGORY_CHOICES = [
        ('tithes', 'Dízimos'),
        ('offerings', 'Ofertas'),
        ('salaries', 'Salários'),
        ('utilities', 'Contas'),
        ('maintenance', 'Manutenção'),
        ('missions', 'Missões'),
        ('events', 'Eventos'),
        ('other', 'Outro'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Dinheiro'),
        ('transfer', 'Transferência'),
        ('card', 'Cartão'),
        ('check', 'Cheque'),
        ('pix', 'PIX'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='finances')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateField()
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES,
                                      blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finances'
        verbose_name = 'Finança'
        verbose_name_plural = 'Finanças'
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.get_type_display()} - {self.category} - R$ {self.amount}"

