from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from payments.models import Payment  # ← Check this line
from django.db.models import Sum, Count
from collections import defaultdict

@login_required
def user_dashboard(request):
    """User dashboard with animal donation stats"""
    # Get all successful donations
    donations = Payment.objects.filter(
        user=request.user,
        status='succeeded'
    ).order_by('-created_at')
    
    # Calculate basic totals
    total_donated = sum(d.amount for d in donations)
    total_donations = donations.count()
    
    # NEW: Get detailed stats per animal
    animal_stats = []
    animal_data = defaultdict(lambda: {'count': 0, 'total': 0})
    
    # Group donations by animal
    for donation in donations:
        if donation.animal:  # Only count donations with animals
            animal = donation.animal
            animal_data[animal]['count'] += 1
            animal_data[animal]['total'] += donation.amount
    
    # Convert to list for template
    for animal, stats in animal_data.items():
        animal_stats.append({
            'animal': animal,
            'donation_count': stats['count'],
            'total_donated': stats['total'],
        })
    
    # Sort by total donated (highest first)
    animal_stats.sort(key=lambda x: x['total_donated'], reverse=True)
    
    context = {
        'donations': donations[:10],  # Show only recent 10
        'total_donated': total_donated,
        'total_donations': total_donations,
        'animal_stats': animal_stats,  # NEW: Animal donation details
        'title': 'My Dashboard',
    }
    return render(request, 'accounts/dashboard.html', context)