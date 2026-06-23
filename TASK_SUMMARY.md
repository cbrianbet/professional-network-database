# Task Summary: Add Diaspora and Profession Bodies Fields

## Completed Work

### Backend Changes
1. **Model Update** (`api/models.py`):
   - Added `diaspora = models.BooleanField(default=False)`
   - Added `profession_bodies = models.JSONField(default=list, blank=True)`

2. **Serializer Update** (`api/serializers.py`):
   - Added `diaspora = serializers.BooleanField(default=False)` to `MemberWriteSerializer`
   - Added `profession_bodies = serializers.ListField(child=serializers.CharField(), default=list)` to `MemberWriteSerializer`

3. **CSV Export Update** (`api/views.py`):
   - Updated `export_members` function to include `diaspora` and `profession_bodies` in CSV columns and data generation

### Frontend Changes
1. **Dashboard Filtering** (`templates/dashboard.html`):
   - Added Diaspora filter dropdown (Any/Yes/No) after Education Level filter
   - Added Profession Bodies text input field after Location filter
   - Updated `normalizeMember` function to include `diaspora` and `profession_bodies` fields
   - Updated `applyFilters` function to filter by diaspora selection and profession_bodies text inclusion
   - Updated `countActiveFilters` function to include the new filter fields

2. **Member Registration Form** (`templates/data-form.html`):
   - Added Diaspora dropdown (Yes/No) after Career/Profession field
   - Added Profession Bodies text input after Diaspora field
   - Updated `fillMemberForm` function to populate diaspora and profession_bodies when editing existing records
   - Updated form submission payload to include diaspora (as boolean) and profession_bodies (as array of strings)

### Database Migration
- Created migration `0010_add_diaspora_and_profession_bodies.py` that adds:
  - `diaspora` BooleanField with default False
  - `profession_bodies` JSONField with default empty list and blank=True

### Dependencies
- Migration depends on `0009_remove_fileresource_api_fileresource_file_type_idx_and_more`

## Verification
All changes have been made and are ready for deployment. The migration file is correctly sequenced and will apply the two new fields to the Member model when executed.

## Next Steps
When the Python service is available, run:
```bash
python manage.py migrate
```

This will apply the new fields to the database schema.