from django.db import models

class Information(models.Model):

    class Meta:
        db_table = "information"

    url = models.URLField(verbose_name='URL',max_length=200)
    email = models.EmailField(verbose_name='メールアドレス',max_length=254)
    user_id = models.IntegerField(verbose_name="ユーザーID")
    
    """
    def __str__(self):
        return "登録済みサイトURL" + self.url +"メールアドレス"+ self.email
    """
