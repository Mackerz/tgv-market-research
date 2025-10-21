# Database Backup Strategy

## Overview

This document outlines the database backup strategy for the TMG Market Research Platform.

## Backup Types

### 1. Automated Cloud SQL Backups (Recommended for Production)

For PostgreSQL on Google Cloud SQL, enable automated backups:

```bash
# Enable automated backups
gcloud sql instances patch market-research-db \
  --backup-start-time=02:00 \
  --backup-location=us-central1 \
  --retained-backups-count=30 \
  --retained-transaction-log-days=7

# Enable Point-in-Time Recovery (PITR)
gcloud sql instances patch market-research-db \
  --enable-point-in-time-recovery \
  --transaction-log-retention-days=7
```

**Features:**
- Automated daily backups at 2 AM
- Retains 30 days of backups
- Point-in-Time Recovery up to 7 days
- Geographic redundancy

**Cost**: ~$0.08/GB/month for backups

### 2. Manual pg_dump Backups

For development or additional backup layers:

```bash
# Create backup directory
mkdir -p /backups/postgres

# Full database backup
pg_dump -h localhost -U postgres -d market_research \
  --format=custom \
  --file="/backups/postgres/backup_$(date +%Y%m%d_%H%M%S).dump"

# Compressed SQL backup
pg_dump -h localhost -U postgres -d market_research \
  | gzip > "/backups/postgres/backup_$(date +%Y%m%d_%H%M%S).sql.gz"
```

### 3. Export to Cloud Storage

Automated script to backup to GCS:

```bash
#!/bin/bash
# backup-to-gcs.sh

# Configuration
DB_NAME="market_research"
DB_USER="postgres"
DB_HOST="localhost"
BUCKET="gs://tmg-backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${DATE}.dump"

# Create backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
  --format=custom \
  --file="/tmp/${BACKUP_FILE}"

# Upload to GCS
gsutil cp "/tmp/${BACKUP_FILE}" "${BUCKET}/${BACKUP_FILE}"

# Cleanup local file
rm "/tmp/${BACKUP_FILE}"

# Delete backups older than 30 days
gsutil ls "${BUCKET}/backup_*.dump" | while read file; do
  file_date=$(echo $file | grep -oP '\d{8}')
  age_days=$(( ($(date +%s) - $(date -d $file_date +%s)) / 86400 ))
  if [ $age_days -gt 30 ]; then
    gsutil rm $file
  fi
done

echo "Backup completed: ${BACKUP_FILE}"
```

Make executable and add to crontab:

```bash
chmod +x backup-to-gcs.sh

# Run daily at 3 AM
crontab -e
0 3 * * * /path/to/backup-to-gcs.sh >> /var/log/db-backup.log 2>&1
```

## Restore Procedures

### Restore from Cloud SQL Backup

```bash
# List available backups
gcloud sql backups list --instance=market-research-db

# Restore from specific backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=market-research-db

# Restore to a specific point in time
gcloud sql backups restore BACKUP_ID \
  --backup-instance=market-research-db \
  --restore-to-timestamp=2025-10-20T15:30:00Z
```

### Restore from pg_dump

```bash
# Drop existing database (WARNING: destructive)
dropdb -h localhost -U postgres market_research

# Create fresh database
createdb -h localhost -U postgres market_research

# Restore from custom format dump
pg_restore -h localhost -U postgres -d market_research \
  --verbose \
  /backups/postgres/backup_20251020_153000.dump

# Or restore from SQL file
gunzip < /backups/postgres/backup_20251020_153000.sql.gz \
  | psql -h localhost -U postgres -d market_research
```

### Restore from GCS

```bash
# Download from GCS
gsutil cp gs://tmg-backups/postgres/backup_20251020_153000.dump /tmp/

# Restore
pg_restore -h localhost -U postgres -d market_research \
  --verbose \
  /tmp/backup_20251020_153000.dump
```

## Backup Testing

Test backups monthly to ensure they're restorable:

```bash
#!/bin/bash
# test-restore.sh

# Create test database
createdb -h localhost -U postgres market_research_test

# Restore latest backup
LATEST_BACKUP=$(ls -t /backups/postgres/*.dump | head -1)
pg_restore -h localhost -U postgres -d market_research_test \
  --verbose \
  $LATEST_BACKUP

# Verify restore
psql -h localhost -U postgres -d market_research_test \
  -c "SELECT COUNT(*) FROM surveys;" \
  -c "SELECT COUNT(*) FROM submissions;" \
  -c "SELECT COUNT(*) FROM responses;"

# Cleanup test database
dropdb -h localhost -U postgres market_research_test

echo "Backup test completed successfully"
```

## Backup Monitoring

### Cloud SQL Backup Monitoring

Set up alerts in Google Cloud Monitoring:

```bash
# Create alert for failed backups
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="DB Backup Failure" \
  --condition-display-name="Backup failed" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=60s \
  --condition-resource-type=cloudsql_database \
  --condition-metric=cloudsql.googleapis.com/database/backup/status
```

### Backup Size Monitoring

Track backup sizes to detect anomalies:

```bash
# Check backup sizes
gsutil du -sh gs://tmg-backups/postgres/*

# Get size of latest backup
LATEST=$(gsutil ls -l gs://tmg-backups/postgres/ | sort -k2 -r | head -2 | tail -1 | awk '{print $1}')
echo "Latest backup size: $LATEST bytes"
```

## Disaster Recovery Plan

### RTO (Recovery Time Objective): 1 hour
- Time to restore database from backup

### RPO (Recovery Point Objective): 24 hours
- Maximum acceptable data loss

### Recovery Steps

1. **Assess the situation**
   - Identify what data was lost or corrupted
   - Determine last known good state

2. **Notify stakeholders**
   - Alert team members
   - Update status page if customer-facing

3. **Create new database instance** (if needed)
   ```bash
   gcloud sql instances create market-research-db-recovery \
     --tier=db-g1-small \
     --region=us-central1
   ```

4. **Restore from backup**
   - Use most recent backup before corruption
   - Verify data integrity after restore

5. **Update connection strings**
   - Point application to recovered database
   - Test application functionality

6. **Document incident**
   - Record what happened
   - Document recovery steps taken
   - Update procedures if needed

## Backup Retention Policy

- **Daily backups**: Retain for 30 days
- **Weekly backups**: Retain for 90 days (first Sunday of each week)
- **Monthly backups**: Retain for 1 year (first Sunday of each month)
- **Annual backups**: Retain for 7 years (regulatory compliance)

### Implementing Retention Policy

```bash
#!/bin/bash
# retention-policy.sh

BUCKET="gs://tmg-backups/postgres"
CURRENT_DATE=$(date +%Y%m%d)

# Tag weekly backups (Sunday)
if [ $(date +%u) -eq 7 ]; then
  gsutil label ch -l backup_type:weekly gs://tmg-backups/postgres/backup_${CURRENT_DATE}_*.dump
fi

# Tag monthly backups (first Sunday)
if [ $(date +%d) -le 7 ] && [ $(date +%u) -eq 7 ]; then
  gsutil label ch -l backup_type:monthly gs://tmg-backups/postgres/backup_${CURRENT_DATE}_*.dump
fi

# Delete daily backups older than 30 days
gsutil ls -L "${BUCKET}/backup_*.dump" | \
  grep -v "backup_type" | \
  # [delete logic here]

# Delete weekly backups older than 90 days
# Delete monthly backups older than 1 year
# [implement similar logic]
```

## Security

- **Encryption at rest**: All Cloud SQL backups are encrypted by default
- **Encryption in transit**: Use SSL/TLS for pg_dump transfers
- **Access control**: Restrict GCS bucket access to service accounts only
- **Audit logging**: Enable Cloud Audit Logs for backup operations

```bash
# Set bucket permissions
gsutil iam ch \
  serviceAccount:backup-service@project-id.iam.gserviceaccount.com:roles/storage.objectAdmin \
  gs://tmg-backups
```

## Backup Checklist

### Daily
- [ ] Verify automated Cloud SQL backup completed
- [ ] Check backup logs for errors
- [ ] Monitor backup storage usage

### Weekly
- [ ] Review backup sizes for anomalies
- [ ] Verify weekly retention tags applied
- [ ] Check GCS bucket storage costs

### Monthly
- [ ] Perform test restore to verify backup integrity
- [ ] Review and update backup procedures
- [ ] Audit backup access logs
- [ ] Document any issues or improvements needed

### Annually
- [ ] Full disaster recovery drill
- [ ] Review and update RPO/RTO targets
- [ ] Audit backup retention compliance
- [ ] Review backup costs and optimize if needed

## Troubleshooting

### Backup fails with "out of disk space"

```bash
# Check disk space
df -h

# Clean up old backups
rm /backups/postgres/backup_*.dump.old

# Increase disk size (Cloud SQL)
gcloud sql instances patch market-research-db --storage-size=50GB
```

### Restore fails with "role does not exist"

```bash
# Create missing roles before restore
createuser -h localhost -U postgres rolename

# Or restore without owner
pg_restore --no-owner -h localhost -U postgres -d market_research backup.dump
```

### Backup takes too long

```bash
# Use parallel dump (PostgreSQL 9.3+)
pg_dump -h localhost -U postgres -d market_research \
  --format=directory \
  --jobs=4 \
  --file=/backups/postgres/backup_parallel/
```

## Resources

- [Cloud SQL Backup Documentation](https://cloud.google.com/sql/docs/postgres/backup-recovery/backing-up)
- [pg_dump Documentation](https://www.postgresql.org/docs/current/app-pgdump.html)
- [PostgreSQL Backup Best Practices](https://www.postgresql.org/docs/current/backup.html)

---

**Last Updated**: 2025-10-21
**Document Owner**: DevOps Team
**Review Frequency**: Quarterly
