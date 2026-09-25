Sample range selection
======================

Both the add-samples form and the dataset edit Samples tab display range controls
above the individual Select2 rows. Choose From, To, and the data resources to link,
then click Add range. Resource choices apply to every sample in the range. Existing
choices are retained; repeated or overlapping ranges merge resource choices into
an existing sample row. Clear range resets only the range controls.

The catalog is the existing SMW response, serialized once with Jinja's `tojson`.
URLs remain sample values. The range algorithm uses the endpoints' indices in
that response, includes both endpoints, and filters to their common family. It
never generates names, fills numerical gaps, or sorts the response. There is no
established cross-prefix range rule in the extension. Conservatively, range
endpoints must have an identical non-digit prefix followed by digits. Other names
remain available through individual selection. This is a range eligibility rule,
not a change to valid SMW page names. The live SMW naming conventions and ordering
should be checked during acceptance testing.

All Select2 controls query the same in-memory catalog, returning 50 matches per
page. Bulk rows use the same sample_linkN, sample_name_N and
sample_resources_listN contract as individual rows; sample_count is the exclusive
upper bound used by the existing helper loops. Endpoints are not submitted or
stored. New URLs are checked against one fresh SMW list per save; existing stored
URLs remain valid during editing even if SMW no longer returns them. Save/edit
permissions and the database schema are unchanged. If SMW is unavailable, new
sample links fail validation; edits containing only stored values still work.

The related edit fixes preserve the stored URL in resource checkbox values and
perform relationship cleanup after processing every submitted row. The count
includes existing edit rows and the final generated row. Duplicate submitted
sample/resource pairs are ignored.

Automated checks (from the extension directory)
-----------------------------------------------

No frontend framework was previously configured. These checks add no runtime
library or test package dependency:

    node --test ckanext/semantic_media_wiki/tests/frontend/sample_range.test.js
    python -m unittest discover -s ckanext/semantic_media_wiki/tests -p test_sample_assignment.py -v

Use the configured project Python interpreter. The Python tests stub only CKAN,
SMW and persistence boundaries and exercise the production helper. They do not
connect to a database or require SMW credentials.

For a DOM integration check with the actual CKAN vendor libraries, run:

    node ckanext/semantic_media_wiki/tests/frontend/browser_check.cjs /path/to/ckan/public/base/vendor /path/to/chrome

This starts a loopback-only fixture server and a temporary headless Chrome
profile. It verifies existing selections, empty ranges, missing IDs, repeated
ranges, merged resources, numbered form serialization, manual editing/removal
of generated rows and clearing endpoints. The fixture is not a full CKAN page.
The seven Node algorithm tests also cover reverse/cross-prefix/unknown endpoints,
manual searches, response ordering, duplicate catalog values and 6000-item paging.
The eight Python tests cover normal/bulk saves, duplicates, invalid URL rejection
before writes, empty values, retained edit records, retired samples and clearing.

Manual acceptance
-----------------

1. Open the add-samples form or the dataset's Samples edit tab. Confirm the order:
   Select sample range; From; To; resource choices; Add range / Clear range;
   Select individual samples; existing individual rows.
2. Search for From X0005 and To X0012. Choose a resource and click Add range.
   Verify each real sample in the range is selected and linked to that resource;
   missing IDs must not appear. Use available same-family endpoints if this site
   does not contain these example IDs.
3. Add the same range again and an overlapping range. Confirm no duplicate rows.
   Choose another resource and repeat; existing resource choices must remain.
4. Add A0001 and B0045 individually, using their resource modals. Change a
   generated sample, edit its resources, and remove a generated row.
5. Verify To offers only the same family at/after From. Change From and confirm
   To clears. Try empty endpoints and confirm a visible validation message.
6. Clear range and confirm assigned samples remain. Save, reopen the Samples
   tab, and check every sample/resource relationship, including the final sample.
   Repeat save without changes and confirm no duplicate relationships.
7. Test editing a dataset with more than 30 existing samples, adding a range
   longer than 30, and searching with the full 5900+ sample catalog. Confirm
   original selections survive and the controls remain responsive.

A live CKAN/SMW save-and-reload check remains required; isolated tests cannot
verify the deployment's database, SMW API limits, theme or web-server form limits.
