# TestStand Integration

This folder will contain the real NI TestStand sequence after the trial is activated.

Planned sequence groups:

- Setup
- Main
- Cleanup

## Daily station verification

The future TestStand sequence will verify the station with the golden reference once per calendar day.

During Setup, TestStand will:

1. Check the stored date/result of the latest successful station verification.
2. Reuse the verification if it was completed successfully today.
3. Run the golden-reference checks only when there is no successful verification for the current day.
4. Block DUT testing if the daily station verification fails.

The verification date/result must be stored persistently so it survives separate DUT sequence runs.

Important: a `.seq` file is not a text placeholder. It should be created and edited with NI TestStand Sequence Editor, then committed here.
