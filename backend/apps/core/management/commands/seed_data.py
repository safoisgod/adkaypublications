"""
Management command: seed_data
Populates the database with realistic sample data for development.

Usage:
    python manage.py seed_data
    python manage.py seed_data --flush    # clear first, then seed
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with sample publishing data.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all existing data before seeding.',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write(self.style.WARNING('Flushing existing data...'))
            self._flush_data()

        self.stdout.write('Seeding data...')

        self._create_superuser()
        self._create_genres()
        self._create_categories_and_tags()
        self._create_services()
        self._create_authors()
        self._create_books()
        self._create_posts()

        self.stdout.write(self.style.SUCCESS('✓ Database seeded successfully.'))

    # ─────────────────────────────────────────────────────────────────────
    def _flush_data(self):
        from apps.books.models import Book, Genre
        from apps.blog.models import Post, Category, Tag
        from apps.authors.models import Author
        from apps.services.models import Service
        Book.objects.all().delete()
        Genre.objects.all().delete()
        Post.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        Author.objects.all().delete()
        Service.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING('All data cleared.'))

    def _create_superuser(self):
        if not User.objects.filter(email='admin@publishinghouse.com').exists():
            User.objects.create_superuser(
                email='admin@publishinghouse.com',
                password='Admin1234!',
                username='admin',
                first_name='Admin',
                last_name='User',
                is_verified=True,
            )
            self.stdout.write(self.style.SUCCESS(
                '  ✓ Superuser created: admin@publishinghouse.com / Admin1234!'
            ))
        else:
            self.stdout.write('  — Superuser already exists, skipping.')

    def _create_genres(self):
        from apps.books.models import Genre
        genres_data = [
            ('Fiction', 'fiction', 1),
            ('Non-Fiction', 'non-fiction', 2),
            ('Biography', 'biography', 3),
            ('Science & Technology', 'science-technology', 4),
            ('History', 'history', 5),
            ('Poetry', 'poetry', 6),
            ('Children\'s', 'childrens', 7),
            ('Self-Help', 'self-help', 8),
        ]
        for name, slug, order in genres_data:
            Genre.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'display_order': order}
            )
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(genres_data)} genres created.'))

    def _create_categories_and_tags(self):
        from apps.blog.models import Category, Tag
        categories = [
            ('Industry News', 'industry-news', '#2563EB', 1),
            ('Author Spotlight', 'author-spotlight', '#7C3AED', 2),
            ('Writing Craft', 'writing-craft', '#059669', 3),
            ('Book Reviews', 'book-reviews', '#DC2626', 4),
            ('Events', 'events', '#D97706', 5),
        ]
        for name, slug, color, order in categories:
            Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'color': color, 'display_order': order}
            )

        tags = [
            'debut-novel', 'literary-fiction', 'prize-winning',
            'translated', 'debut-author', 'short-stories',
            'writing-tips', 'publishing-industry', 'book-club',
        ]
        for tag_slug in tags:
            name = tag_slug.replace('-', ' ').title()
            Tag.objects.get_or_create(slug=tag_slug, defaults={'name': name})

        self.stdout.write(self.style.SUCCESS(
            f'  ✓ {len(categories)} categories, {len(tags)} tags created.'
        ))

    def _create_services(self):
        from apps.services.models import Service
        services = [
            {
                'title': 'Manuscript Editing',
                'slug': 'manuscript-editing',
                'icon': 'edit',
                'short_description': 'Professional structural, line, and copy editing by our senior editorial team.',
                'full_description': '<p>Our editorial team works closely with authors at every level of the manuscript.</p>',
                'features': '["Developmental editing", "Line editing", "Copy editing", "Proofreading"]',
                'is_featured': True,
                'display_order': 1,
            },
            {
                'title': 'Book Design & Production',
                'slug': 'book-design-production',
                'icon': 'layers',
                'short_description': 'Award-winning cover design and interior typesetting.',
                'full_description': '<p>From concept to finished book, our design studio creates visually stunning results.</p>',
                'features': '["Cover design", "Interior typesetting", "eBook formatting", "Print-ready files"]',
                'is_featured': True,
                'display_order': 2,
            },
            {
                'title': 'Rights & Distribution',
                'slug': 'rights-distribution',
                'icon': 'globe',
                'short_description': 'Global rights management and distribution across all major channels.',
                'full_description': '<p>Our rights team pursues translation deals in over 40 territories worldwide.</p>',
                'features': '["Translation rights", "Foreign rights", "Digital distribution", "Library supply"]',
                'is_featured': True,
                'display_order': 3,
            },
            {
                'title': 'Marketing & Publicity',
                'slug': 'marketing-publicity',
                'icon': 'megaphone',
                'short_description': 'Strategic campaigns and digital marketing to maximise your book\'s reach.',
                'full_description': '<p>Our publicity team crafts bespoke campaigns for every title.</p>',
                'features': '["Press releases", "Social media strategy", "Influencer outreach", "Launch events"]',
                'is_featured': False,
                'display_order': 4,
            },
        ]
        for s in services:
            Service.objects.get_or_create(slug=s['slug'], defaults=s)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(services)} services created.'))

    def _create_authors(self):
        from apps.authors.models import Author
        authors_data = [
            {
                'full_name': 'Eleanor Ashford',
                'slug': 'eleanor-ashford',
                'role': 'Literary Fiction Author',
                'short_bio': 'Award-winning author of five novels exploring memory, identity, and belonging.',
                'bio': 'Eleanor Ashford is the author of five internationally acclaimed novels. Her work has been translated into 28 languages and has won numerous literary prizes. She lives between London and Lisbon.',
                'twitter': 'https://twitter.com/eleanor_ashford',
                'is_featured': True,
                'display_order': 1,
            },
            {
                'full_name': 'Marcus J. Cole',
                'slug': 'marcus-j-cole',
                'role': 'Science & Technology Writer',
                'short_bio': 'Former MIT professor turned science communicator and bestselling author.',
                'bio': 'Marcus J. Cole spent fifteen years at MIT before turning to full-time writing. His books make complex scientific concepts accessible and thrilling to general audiences.',
                'linkedin': 'https://linkedin.com/in/marcusjcole',
                'is_featured': True,
                'display_order': 2,
            },
            {
                'full_name': 'Amara Osei',
                'slug': 'amara-osei',
                'role': 'Historical Fiction Author',
                'short_bio': 'Ghanaian-British author weaving untold histories into vivid fiction.',
                'bio': 'Amara Osei was born in Accra and raised in Bristol. Her debut novel was longlisted for the Booker Prize. She lectures in creative writing at Bristol University.',
                'twitter': 'https://twitter.com/amara_osei',
                'instagram': 'https://instagram.com/amara_osei_writes',
                'is_featured': True,
                'display_order': 3,
            },
            {
                'full_name': 'Dr. Petra Voss',
                'slug': 'dr-petra-voss',
                'role': 'Non-Fiction & Essays',
                'short_bio': 'Cultural critic, essayist, and author of three acclaimed non-fiction works.',
                'bio': 'Dr. Petra Voss is a cultural critic whose essays appear in publications worldwide. Her books interrogate contemporary culture with precision and wit.',
                'website': 'https://petravoss.com',
                'is_featured': True,
                'display_order': 4,
            },
            {
                'full_name': 'James Thornton',
                'slug': 'james-thornton',
                'role': 'Thriller & Crime Author',
                'short_bio': 'Former journalist whose gripping thrillers have sold over 2 million copies.',
                'bio': 'James Thornton spent twelve years as an investigative journalist before writing his debut thriller. He now writes full-time from Edinburgh.',
                'twitter': 'https://twitter.com/jamesthornton_writes',
                'is_featured': False,
                'display_order': 5,
            },
            {
                'full_name': 'Yuki Tanaka',
                'slug': 'yuki-tanaka',
                'role': 'Children\'s & Young Adult Author',
                'short_bio': 'Beloved author of the Starlight Chronicles series for young readers.',
                'bio': 'Yuki Tanaka has written over twenty books for children and young adults. The Starlight Chronicles series has sold millions of copies across 30 countries.',
                'instagram': 'https://instagram.com/yukitanaka_books',
                'is_featured': False,
                'display_order': 6,
            },
        ]
        for a in authors_data:
            Author.objects.get_or_create(slug=a['slug'], defaults=a)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(authors_data)} authors created.'))

    def _create_books(self):
        from apps.books.models import Book, Genre
        from apps.authors.models import Author

        try:
            fiction = Genre.objects.get(slug='fiction')
            nonfiction = Genre.objects.get(slug='non-fiction')
            history = Genre.objects.get(slug='history')
            scifi = Genre.objects.get(slug='science-technology')
            biography = Genre.objects.get(slug='biography')

            eleanor = Author.objects.get(slug='eleanor-ashford')
            marcus = Author.objects.get(slug='marcus-j-cole')
            amara = Author.objects.get(slug='amara-osei')
            petra = Author.objects.get(slug='dr-petra-voss')
            james = Author.objects.get(slug='james-thornton')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Could not fetch genres/authors: {e}'))
            return

        books_data = [
            {
                'title': 'The Light Between Tides',
                'slug': 'the-light-between-tides',
                'subtitle': 'A Novel of Loss and Return',
                'genre': fiction,
                'description': '<p>A luminous novel about a woman returning to the coastal town of her childhood after twenty years away, uncovering the truth about a disappearance that changed everything.</p>',
                'excerpt': 'A luminous novel about memory, loss, and the courage to return.',
                'publisher': 'Publishing House',
                'published_date': '2024-03-15',
                'pages': 312,
                'price': '14.99',
                'is_featured': True,
                'is_published': True,
                'is_new_release': True,
                'author_obj': eleanor,
            },
            {
                'title': 'The Quantum Paradox',
                'slug': 'the-quantum-paradox',
                'subtitle': 'Understanding the Universe\'s Strangest Secrets',
                'genre': scifi,
                'description': '<p>A breathtaking journey through the counterintuitive world of quantum mechanics, written for the curious non-scientist.</p>',
                'excerpt': 'The universe is stranger than we dare imagine — and Marcus J. Cole is the perfect guide.',
                'publisher': 'Publishing House',
                'published_date': '2024-01-20',
                'pages': 287,
                'price': '16.99',
                'is_featured': True,
                'is_published': True,
                'is_bestseller': True,
                'author_obj': marcus,
            },
            {
                'title': 'Rivers of Gold',
                'slug': 'rivers-of-gold',
                'subtitle': 'A Story of Empire and Resistance',
                'genre': history,
                'description': '<p>Set across three continents in the late nineteenth century, this sweeping historical novel follows four characters whose lives are bound together by colonialism, trade, and resistance.</p>',
                'excerpt': 'A sweeping, urgent novel that reclaims silenced histories.',
                'publisher': 'Publishing House',
                'published_date': '2023-09-05',
                'pages': 428,
                'price': '15.99',
                'is_featured': True,
                'is_published': True,
                'is_bestseller': True,
                'author_obj': amara,
            },
            {
                'title': 'The Attention Economy',
                'slug': 'the-attention-economy',
                'subtitle': 'How Tech Companies Hijacked Our Minds',
                'genre': nonfiction,
                'description': '<p>A sharp and essential analysis of how digital platforms manipulate human attention, and what we can do to reclaim our mental sovereignty.</p>',
                'excerpt': 'Essential reading for anyone who has ever felt owned by their phone.',
                'publisher': 'Publishing House',
                'published_date': '2023-11-12',
                'pages': 256,
                'price': '13.99',
                'is_featured': False,
                'is_published': True,
                'is_new_release': False,
                'author_obj': petra,
            },
            {
                'title': 'The Last Signal',
                'slug': 'the-last-signal',
                'subtitle': 'A Thriller',
                'genre': fiction,
                'description': '<p>When a veteran cryptographer receives an impossible message from a dead colleague, she is drawn into a conspiracy that spans four governments and thirty years.</p>',
                'excerpt': 'Taut, propulsive and utterly gripping — Thornton\'s finest yet.',
                'publisher': 'Publishing House',
                'published_date': '2024-02-08',
                'pages': 368,
                'price': '14.99',
                'is_featured': False,
                'is_published': True,
                'is_new_release': True,
                'author_obj': james,
            },
            {
                'title': 'Before the Storm',
                'slug': 'before-the-storm',
                'subtitle': 'Stories',
                'genre': fiction,
                'description': '<p>A luminous debut collection of short stories set across West Africa and Britain, tracing the threads that connect families across generations and oceans.</p>',
                'excerpt': 'Devastating and beautiful — a debut that announces a major new voice.',
                'publisher': 'Publishing House',
                'published_date': '2023-06-20',
                'pages': 224,
                'price': '12.99',
                'is_featured': True,
                'is_published': True,
                'is_bestseller': False,
                'author_obj': amara,
            },
        ]

        for b in books_data:
            author_obj = b.pop('author_obj')
            slug = b['slug']
            book, created = Book.objects.get_or_create(slug=slug, defaults=b)
            if created:
                book.authors.add(author_obj)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(books_data)} books created.'))

    def _create_posts(self):
        from apps.blog.models import Post, Category, Tag
        try:
            industry = Category.objects.get(slug='industry-news')
            spotlight = Category.objects.get(slug='author-spotlight')
            craft = Category.objects.get(slug='writing-craft')
            admin_user = User.objects.filter(is_superuser=True).first()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Could not fetch categories: {e}'))
            return

        posts_data = [
            {
                'title': 'The Future of Independent Publishing',
                'slug': 'future-of-independent-publishing',
                'excerpt': 'As major conglomerates consolidate, independent publishers are finding creative ways to thrive — and redefine what publishing can be.',
                'body': '<p>The publishing landscape has shifted dramatically over the past decade. With five major corporations now controlling the majority of traditional publishing, independent houses have had to innovate or perish.</p><p>Yet the independents are thriving in unexpected ways. From direct-to-reader subscription models to micro-targeted niche catalogues, the indie sector is growing faster than the mainstream.</p>',
                'category': industry,
                'author': admin_user,
                'is_published': True,
                'is_featured': True,
                'published_at': timezone.now() - timedelta(days=2),
            },
            {
                'title': 'A Conversation with Eleanor Ashford',
                'slug': 'conversation-with-eleanor-ashford',
                'excerpt': 'The author of The Light Between Tides talks about grief, creative process, and why she spent three years living by the sea to write her latest novel.',
                'body': '<p>"I needed to understand what it feels like to wait," Eleanor Ashford tells me, sitting in the garden of her Lisbon apartment. "The protagonist spends twenty years waiting — for answers, for permission to grieve, for herself. I couldn\'t write that from a desk in London."</p><p>The result is her most personal and most accomplished novel yet.</p>',
                'category': spotlight,
                'author': admin_user,
                'is_published': True,
                'is_featured': True,
                'published_at': timezone.now() - timedelta(days=5),
            },
            {
                'title': 'Five Ways to Deepen Your Characters',
                'slug': 'five-ways-to-deepen-your-characters',
                'excerpt': 'Memorable characters are not invented — they are excavated. Here are five techniques for finding the truth at the core of every person in your story.',
                'body': '<p>The most common craft problem I encounter when editing manuscripts is characters who feel constructed rather than discovered. The author knows what they want the character to do, so the character does it. But readers can sense the mechanism.</p><p>Here are five techniques that help writers move from construction to excavation.</p><h2>1. Write Their Contradictions</h2><p>Real people contain multitudes. A generous man can be petty. A brave woman can be a coward at home. Build your character around their central contradiction.</p>',
                'category': craft,
                'author': admin_user,
                'is_published': True,
                'is_featured': False,
                'published_at': timezone.now() - timedelta(days=10),
            },
            {
                'title': 'AI in Publishing: Threat or Tool?',
                'slug': 'ai-in-publishing-threat-or-tool',
                'excerpt': 'The industry is divided on generative AI. We spoke with editors, agents, and authors to understand where the real risks — and opportunities — lie.',
                'body': '<p>Walk into any publishing conference in 2024 and the conversation invariably turns to AI. Some see existential threat; others see opportunity. Most are simply confused.</p><p>The reality, as ever, is more nuanced than the headlines suggest.</p>',
                'category': industry,
                'author': admin_user,
                'is_published': True,
                'is_featured': True,
                'published_at': timezone.now() - timedelta(days=14),
            },
        ]

        for p in posts_data:
            Post.objects.get_or_create(slug=p['slug'], defaults=p)

        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(posts_data)} blog posts created.'))
