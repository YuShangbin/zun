#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_log import log as logging
import pecan

from zun.api.controllers import base
from zun.api.controllers.v1 import collection
from zun.api.controllers.v1.views import hosts_view as view
from zun.api import utils as api_utils
from zun.common import exception
from zun.common import policy
from zun import objects

LOG = logging.getLogger(__name__)


class HostCollection(collection.Collection):
    """API representation of a collection of hosts."""

    fields = {
        'hosts',
        'next'
    }

    """A list containing compute node objects"""

    def __init__(self, **kwargs):
        super(HostCollection, self).__init__(**kwargs)
        self._type = 'hosts'

    @staticmethod
    def convert_with_links(nodes, limit, url=None,
                           expand=False, **kwargs):
        collection = HostCollection()
        collection.hosts = [view.format_host(url, p) for p in nodes]
        collection.next = collection.get_next(limit, url=url, **kwargs)
        return collection


class HostController(base.Controller):
    """Host info controller"""

    @pecan.expose('json')
    @base.Controller.api_version("1.4")
    @exception.wrap_pecan_controller_exception
    def get_all(self, **kwargs):
        """Retrieve a list of hosts"""
        context = pecan.request.context
        policy.enforce(context, "host:get_all",
                       action="host:get_all")
        return self._get_host_collection(**kwargs)

    def _get_host_collection(self, **kwargs):
        context = pecan.request.context
        limit = api_utils.validate_limit(kwargs.get('limit'))
        sort_dir = api_utils.validate_sort_dir(kwargs.get('sort_dir', 'asc'))
        sort_key = kwargs.get('sort_key', 'hostname')
        expand = kwargs.get('expand')
        filters = None
        marker_obj = None
        resource_url = kwargs.get('resource_url')
        marker = kwargs.get('marker')
        if marker:
            marker_obj = objects.ComputeNode.get_by_uuid(context, marker)
        nodes = objects.ComputeNode.list(context,
                                         limit,
                                         marker_obj,
                                         sort_key,
                                         sort_dir,
                                         filters=filters)
        return HostCollection.convert_with_links(nodes, limit,
                                                 url=resource_url,
                                                 expand=expand,
                                                 sort_key=sort_key,
                                                 sort_dir=sort_dir)
