
kwargs.pop('timeout', None)
kwargs.pop('raise_on_any_failure', True)
kwargs.pop('delete_snapshots', None)
kwargs.pop('if_modified_since', None)
kwargs.pop('if_unmodified_since', None)
kwargs.pop('if_tags_match_condition', None)
kwargs.update({'raise_on_any_failure': raise_on_any_failure, 'sas': self._query_str.replace('?', '&'), 'timeout': (('&timeout=' + str(timeout)) if timeout else ''), 'path': self.container_name, 'restype': 'restype=container&'})
[]
for blob in blobs:
    _get_blob_name(blob)
    self.container_name
    try:
        BlobClient._generic_delete_blob_options(snapshot=blob.get('snapshot'), delete_snapshots=(delete_snapshots or blob.get('delete_snapshots')), lease=blob.get('lease_id'), if_modified_since=(if_modified_since or blob.get('if_modified_since')), if_unmodified_since=(if_unmodified_since or blob.get('if_unmodified_since')), etag=blob.get('etag'), if_tags_match_condition=(if_tags_match_condition or blob.get('if_tags_match_condition')), match_condition=((blob.get('match_condition') or MatchConditions.IfNotModified) if blob.get('etag') else None), timeout=blob.get('timeout'))
    except AttributeError:
        BlobClient._generic_delete_blob_options(delete_snapshots=delete_snapshots, if_modified_since=if_modified_since, if_unmodified_since=if_unmodified_since, if_tags_match_condition=if_tags_match_condition)
    (query_parameters, header_parameters) = self._generate_delete_blobs_subrequest_options(**options)
    HttpRequest('DELETE', '/{}/{}{}'.format(quote(container_name), quote(blob_name, safe='/~'), self._query_str), headers=header_parameters)
    req.format_parameters(query_parameters)
    reqs.append(req)
