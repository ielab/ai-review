import uuid
import logging
from django.core.management.base import BaseCommand, CommandError
from review.models import Review
from django.utils import timezone

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Migrate reviews between page-based and study-centric structures'

    def add_arguments(self, parser):
        parser.add_argument('review_id', nargs='?', type=int, help='The ID of the review to migrate')
        
        parser.add_argument(
            '--all',
            action='store_true',
            help='Migrate all reviews',
        )
        
        parser.add_argument(
            '--target',
            type=str,
            choices=['page_based', 'study_centric'],
            help='Target structure to migrate to',
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without making changes',
        )

    def handle(self, *args, **options):
        review_id = options.get('review_id')
        migrate_all = options.get('all')
        target_structure = options.get('target')
        dry_run = options.get('dry_run')
        
        # Check that either review_id or --all is provided
        if not review_id and not migrate_all:
            raise CommandError('You must provide either a review_id or the --all flag')
            
        # Check that target structure is provided
        if not target_structure:
            raise CommandError('You must provide a target structure (--target=page_based or --target=study_centric)')
            
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in dry-run mode. No changes will be made.'))
            
        # Get the reviews to migrate
        if migrate_all:
            reviews = Review.objects.all()
            self.stdout.write(f'Found {reviews.count()} reviews to process')
        else:
            try:
                reviews = [Review.objects.get(id=review_id)]
                self.stdout.write(f'Processing review ID {review_id}')
            except Review.DoesNotExist:
                raise CommandError(f'Review with ID {review_id} does not exist')
                
        # Process each review
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        for review in reviews:
            # Skip if already in target structure
            if review.structure_type == target_structure:
                self.stdout.write(self.style.WARNING(
                    f'Review ID {review.id} already uses {target_structure} structure. Skipping.'
                ))
                skipped_count += 1
                continue
                
            # Migrate structure
            try:
                if target_structure == 'page_based':
                    self._migrate_to_page_based(review, dry_run)
                else:  # target_structure == 'study_centric'
                    self._migrate_to_study_centric(review, dry_run)
                    
                if not dry_run:
                    review.structure_type = target_structure
                    review.updated_at = timezone.now()
                    review.save()
                    
                success_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully migrated review ID {review.id} to {target_structure} structure'
                ))
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(
                    f'Error migrating review ID {review.id}: {str(e)}'
                ))
                logger.error(f'Error migrating review ID {review.id}: {str(e)}', exc_info=True)
                
        # Print summary
        self.stdout.write(self.style.SUCCESS(
            f'Migration complete. Success: {success_count}, Errors: {error_count}, Skipped: {skipped_count}'
        ))
        
    def _migrate_to_page_based(self, review, dry_run=False):
        """
        Migrate a review from study-centric to page-based structure.
        
        Args:
            review: The Review object to migrate
            dry_run: If True, don't apply changes
        """
        if not review.screening_pages or "studies" not in review.screening_pages:
            raise CommandError(f'Review ID {review.id} has no studies to migrate')
            
        # Get all studies
        studies = review.screening_pages.get("studies", [])
        
        # Initialize page-based structure
        page_based = {"pages": []}
        page_size = review.show_docs_per_page
        
        # Group studies into pages
        for i in range(0, len(studies), page_size):
            page_studies = studies[i: i + page_size]
            page_index = i // page_size
            
            # Remove study_id field from each study
            for study in page_studies:
                if "study_id" in study:
                    del study["study_id"]
                    
            page_entry = {
                "page_index": page_index,
                "studies": page_studies
            }
            page_based["pages"].append(page_entry)
            
        # Save if not dry run
        if not dry_run:
            review.screening_pages = page_based
            
        return page_based
            
    def _migrate_to_study_centric(self, review, dry_run=False):
        """
        Migrate a review from page-based to study-centric structure.
        
        Args:
            review: The Review object to migrate
            dry_run: If True, don't apply changes
        """
        if not review.screening_pages or "pages" not in review.screening_pages:
            raise CommandError(f'Review ID {review.id} has no pages to migrate')
            
        # Initialize study-centric structure
        study_centric = {"studies": []}
        
        # Extract all studies from all pages
        for page in review.screening_pages.get("pages", []):
            for study in page.get("studies", []):
                # Add study_id field to each study
                if "pmid" in study:
                    study["study_id"] = study["pmid"]
                else:
                    # Generate a unique ID if no pmid exists
                    study["study_id"] = f"s-{uuid.uuid4()}"
                    
                # Add to flat list
                study_centric["studies"].append(study)
                
        # Save if not dry run
        if not dry_run:
            review.screening_pages = study_centric
            
        return study_centric 