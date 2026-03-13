from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='assignments.Submission')
def give_coin_for_grade(sender, instance, created, **kwargs):
    """
    Baho qo'yilganida coin berish
    faqat status='graded' bo'lganda ishlaydi
    """
    if not created and instance.status == 'graded' and instance.score is not None:
        from apps.coins.services import award_grade_coin
        award_grade_coin(instance)