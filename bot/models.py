from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens", verbose_name="Token Owner", help_text="User who owns this token")
    token_symbol = models.CharField(max_length=20, unique=True, verbose_name="Token Symbol", help_text="Symbol of the token (e.g., BTC, ETH)")
    token_name = models.CharField(max_length=100,  verbose_name="Token Name", help_text="Full name of the token (e.g., Bitcoin, Ethereum)")
    exchange = models.CharField(max_length=50, verbose_name="Exchange Platform", help_text="Exchange where the token is listed (e.g., Binance, Coinbase)")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the token was added")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the token was last updated")

    def __str__(self):
        return f"{self.token_name} ({self.token_symbol}) - Owned by {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Token"
        verbose_name_plural = "Tokens"
