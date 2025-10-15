from django.shortcuts import render


def home(request):
    """Homepage view"""
    context = {
        'company_name': 'Diaspora Enterprise',
        'tagline': 'Your partner in real estate investments and short-term rentals',
    }
    return render(request, 'website/home.html', context)


def team(request):
    """Team page view"""
    team_members = [
        {
            'name': 'Marvens King',
            'title': 'CEO',
            'initials': 'MK'
        },
        {
            'name': 'Carlos Rado',
            'title': 'President',
            'initials': 'CR'
        },
        {
            'name': 'Sherifa Siddeeq',
            'title': 'COO',
            'initials': 'SS'
        },
        {
            'name': 'Alicia Ramdhan',
            'title': 'CFO',
            'initials': 'AR'
        },
    ]
    context = {
        'team_members': team_members,
    }
    return render(request, 'website/team.html', context)


def story(request):
    """Our Story page view"""
    context = {}
    return render(request, 'website/story.html', context)
