"""OpenFlow 1.3 OXM match fields.
Flow's match is very different from OF 1.0. Instead of always having all
fields, there's a variable list of match fields and each one is an Openflow
eXtended Match Type-Length-Value (OXM TLV) element.
This module provides high-level Python classes for OXM TLV fields in order to
make the OF 1.3 match fields easy to use and to be coded.
"""
from abc import ABC, abstractmethod

from pyof.foundation.basic_types import HWAddress, IPAddress
from pyof.v0x04.common.flow_match import OxmOfbMatchField, OxmTLV, VlanId

from napps.kytos.of_core.v0x04.utils import bytes_to_mask, mask_to_bytes


class MatchField(ABC):
    """Base class for match fields. Abstract OXM TLVs of python-openflow.
    Just extend this class and you will be forced to define the required
    low-level attributes and methods below:
    * "name" attribute (field name to be displayed in JSON);
    * "oxm_field" attribute (``OxmOfbMatchField`` enum);
    * Method to return a pyof OxmTLV;
    * Method to create an instance from an OxmTLV.
    """

    def __init__(self, value):
        """Define match field value."""
        self.value = value

    @property
    @classmethod
    @abstractmethod
    def name(cls):
        """Define a name to be displayed in JSON.
        It can be overriden just by a class attibute.
        """

    @property
    @classmethod
    @abstractmethod
    def oxm_field(cls):
        """Define this subclass ``OxmOfbMatchField`` value.
        It can be overriden just by as a class attibute.
        """

    @abstractmethod
    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""

    @classmethod
    @abstractmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""

    def __eq__(self, other):
        """Two objects are equal if their values are the same.
        The oxm_field equality is checked indirectly when comparing whether
        the objects are instances of the same class.
        """
        return isinstance(other, self.__class__) and other.value == self.value


class MatchDLVLAN(MatchField):
    """Match for datalink VLAN ID."""

    name = 'dl_vlan'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_VLAN_VID

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        try:
            value = int(self.value)
            mask = None
            oxm_hasmask = False
        except ValueError:
            value, mask = map(int, self.value.split('/'))
            oxm_hasmask = True
        value = value | VlanId.OFPVID_PRESENT
        value_bytes = value.to_bytes(2, 'big')
        if mask:
            mask = mask | VlanId.OFPVID_PRESENT
            value_bytes += mask.to_bytes(2, 'big')
        return OxmTLV(oxm_field=self.oxm_field,
                      oxm_hasmask=oxm_hasmask,
                      oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        vlan_id = int.from_bytes(tlv.oxm_value[:2], 'big') & 4095
        value = vlan_id
        if tlv.oxm_hasmask:
            vlan_mask = int.from_bytes(tlv.oxm_value[2:], 'big') & 4095
            value = f'{vlan_id}/{vlan_mask}'
        return cls(value)


class MatchDLVLANPCP(MatchField):
    """Match for VLAN Priority Code Point."""

    name = 'dl_vlan_pcp'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_VLAN_PCP

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(1, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        priority = int.from_bytes(tlv.oxm_value, 'big')
        return cls(priority)


class MatchDLSrc(MatchField):
    """Match for datalink source."""

    name = 'dl_src'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_ETH_SRC

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        if '/' in self.value:
            value, mask = self.value.split('/')
            if mask.upper() == 'FF:FF:FF:FF:FF:FF':
                mask = None
                oxm_hasmask = False
            else:
                mask = mask.upper()
                oxm_hasmask = True
        else:
            value = self.value
            mask = None
            oxm_hasmask = False
        value_bytes = HWAddress(value).pack()
        if mask:
            value_bytes += HWAddress(mask).pack()
        return OxmTLV(oxm_field=self.oxm_field,
                      oxm_hasmask=oxm_hasmask,
                      oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        hw_address = HWAddress()
        hw_address.unpack(tlv.oxm_value)
        addr_str = str(hw_address)
        value = addr_str
        if tlv.oxm_hasmask:
            hw_mask = HWAddress()
            hw_mask.unpack(tlv.oxm_value[6:])
            mask_str = str(hw_mask)
            value = f'{addr_str}/{mask_str}'
        return cls(value)


class MatchDLDst(MatchField):
    """Match for datalink destination."""

    name = 'dl_dst'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_ETH_DST

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        if '/' in self.value:
            value, mask = self.value.split('/')
            if mask.upper() == 'FF:FF:FF:FF:FF:FF':
                mask = None
                oxm_hasmask = False
            else:
                mask = mask.upper()
                oxm_hasmask = True
        else:
            value = self.value
            mask = None
            oxm_hasmask = False
        value_bytes = HWAddress(value).pack()
        if mask:
            value_bytes += HWAddress(mask).pack()
        return OxmTLV(oxm_field=self.oxm_field,
                      oxm_hasmask=oxm_hasmask,
                      oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        hw_address = HWAddress()
        hw_address.unpack(tlv.oxm_value)
        addr_str = str(hw_address)
        value = addr_str
        if tlv.oxm_hasmask:
            hw_mask = HWAddress()
            hw_mask.unpack(tlv.oxm_value[6:])
            mask_str = str(hw_mask)
            value = f'{addr_str}/{mask_str}'
        return cls(value)


class MatchDLType(MatchField):
    """Match for datalink type."""

    name = 'dl_type'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_ETH_TYPE

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(2, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        port = int.from_bytes(tlv.oxm_value, 'big')
        return cls(port)


class MatchNwSrc(MatchField):
    """Match for IPV4 source."""

    name = 'nw_src'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_IPV4_SRC

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        ip_addr = IPAddress(self.value)
        value_bytes = ip_addr.pack()
        if ip_addr.netmask < 32:
            value_bytes += mask_to_bytes(ip_addr.netmask, 32)
        return OxmTLV(oxm_field=self.oxm_field,
                      oxm_hasmask=ip_addr.netmask < 32,
                      oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        ip_address = IPAddress()
        ip_address.unpack(tlv.oxm_value)
        addr_str = str(ip_address)
        value = addr_str
        if tlv.oxm_hasmask:
            value = f'{addr_str}/{bytes_to_mask(tlv.oxm_value[4:], 32)}'
        return cls(value)


class MatchNwDst(MatchField):
    """Match for IPV4 destination."""

    name = 'nw_dst'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_IPV4_DST

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        ip_addr = IPAddress(self.value)
        value_bytes = ip_addr.pack()
        if ip_addr.netmask < 32:
            value_bytes += mask_to_bytes(ip_addr.netmask, 32)
        return OxmTLV(oxm_field=self.oxm_field,
                      oxm_hasmask=ip_addr.netmask < 32,
                      oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        ip_address = IPAddress()
        ip_address.unpack(tlv.oxm_value)
        addr_str = str(ip_address)
        value = addr_str
        if tlv.oxm_hasmask:
            value = f'{addr_str}/{bytes_to_mask(tlv.oxm_value[4:], 32)}'
        return cls(value)


class MatchNwProto(MatchField):
    """Match for IP protocol."""

    name = 'nw_proto'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_IP_PROTO

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(1, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        priority = int.from_bytes(tlv.oxm_value, 'big')
        return cls(priority)


class MatchInPort(MatchField):
    """Match for input port."""

    name = 'in_port'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_IN_PORT

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(4, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        port = int.from_bytes(tlv.oxm_value, 'big')
        return cls(port)


class MatchTCPSrc(MatchField):
    """Match for TCP source."""

    name = 'tp_src'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_TCP_SRC

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(2, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        port = int.from_bytes(tlv.oxm_value, 'big')
        return cls(port)


class MatchTCPDst(MatchField):
    """Match for TCP destination."""

    name = 'tp_dst'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_TCP_DST

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(2, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        port = int.from_bytes(tlv.oxm_value, 'big')
        return cls(port)


class MatchInPhyPort(MatchField):
    """Match for physical input port."""

    name = 'in_phy_port'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_IN_PHY_PORT

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(4, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        port = int.from_bytes(tlv.oxm_value, 'big')
        return cls(port)


class MatchIPDSCP(MatchField):
    """Match for IP DSCP."""

    name = 'ip_dscp'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_IP_DSCP

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(1, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        value = int.from_bytes(tlv.oxm_value, 'big')
        return cls(value)


class MatchIPECN(MatchField):
    """Match for IP ECN."""

    name = 'ip_ecn'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_IP_ECN

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(1, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        value = int.from_bytes(tlv.oxm_value, 'big')
        return cls(value)


class MatchUDPSrc(MatchField):
    """Match for UDP source."""

    name = 'udp_src'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_UDP_SRC

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(2, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        port = int.from_bytes(tlv.oxm_value, 'big')
        return cls(port)


class MatchUDPDst(MatchField):
    """Match for UDP destination."""

    name = 'udp_dst'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_UDP_DST

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(2, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        port = int.from_bytes(tlv.oxm_value, 'big')
        return cls(port)


class MatchICMPV4Type(MatchField):
    """Match for ICMPV4 type."""

    name = 'icmpv4_type'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_ICMPV4_TYPE

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(1, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        port = int.from_bytes(tlv.oxm_value, 'big')
        return cls(port)


class MatchICMPV4Code(MatchField):
    """Match for ICMPV4 code."""

    name = 'icmpv4_code'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_ICMPV4_CODE

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(1, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        priority = int.from_bytes(tlv.oxm_value, 'big')
        return cls(priority)


class MatchARPOP(MatchField):
    """Match for ARP opcode."""

    name = 'arp_op'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_ARP_OP

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(2, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        opcode = int.from_bytes(tlv.oxm_value, 'big')
        return cls(opcode)


class MatchIVP6FLabel(MatchField):
    """Match for IPV6 Flow Label."""

    name = 'ipv6_flabel'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_IPV6_FLABEL

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        try:
            value = int(self.value)
            mask = None
            oxm_hasmask = False
        except ValueError:
            value, mask = map(int, self.value.split('/'))
            oxm_hasmask = True
        value_bytes = value.to_bytes(4, 'big')
        if mask:
            value_bytes += mask.to_bytes(4, 'big')
        return OxmTLV(oxm_field=self.oxm_field,
                      oxm_hasmask=oxm_hasmask,
                      oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        value = int.from_bytes(tlv.oxm_value[:4], 'big')
        if tlv.oxm_hasmask:
            flabel_mask = int.from_bytes(tlv.oxm_value[4:], 'big')
            value = f'{value}/{flabel_mask}'
        return cls(value)


class MatchICMPV6Type(MatchField):
    """Match for ICMPV6 type."""

    name = 'icmpv6_type'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_ICMPV6_TYPE

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(1, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        port = int.from_bytes(tlv.oxm_value, 'big')
        return cls(port)


class MatchICMPV6Code(MatchField):
    """Match for ICMPV6 code."""

    name = 'icmpv6_code'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_ICMPV6_CODE

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(1, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        priority = int.from_bytes(tlv.oxm_value, 'big')
        return cls(priority)


class MatchNDTarget(MatchField):
    """Match for IPV6 ND Target."""

    name = 'nd_tar'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_IPV6_ND_TARGET

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(16, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        target = int.from_bytes(tlv.oxm_value, 'big')
        return cls(target)


class MatchNDSLL(MatchField):
    """Match for IPV6 ND SLL."""

    name = 'nd_sll'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_IPV6_ND_SLL

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(6, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        sll = int.from_bytes(tlv.oxm_value, 'big')
        return cls(sll)


class MatchNDTLL(MatchField):
    """Match for IPV6 ND TLL."""

    name = 'nd_tll'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_IPV6_ND_TLL

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(6, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        tll = int.from_bytes(tlv.oxm_value, 'big')
        return cls(tll)

class MatchMPLSLabel(MatchField):
    """Match for MPLS Label"""

    name = 'mpls_lab'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_MPLS_LABEL

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        value_bytes = self.value.to_bytes(4, 'big')
        return OxmTLV(oxm_field=self.oxm_field, oxm_value=value_bytes)
    
    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        lab = int.from_bytes(tlv.oxm_value, 'big')
        return cls(lab)

class MatchPBBISID(MatchField):
    """Match for PBB ISID."""

    name = 'pbb_isid'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_PBB_ISID

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        try:
            value = int(self.value)
            mask = None
            oxm_hasmask = False
        except ValueError:
            value, mask = map(int, self.value.split('/'))
            oxm_hasmask = True
        value_bytes = value.to_bytes(3, 'big')
        if mask:
            value_bytes += mask.to_bytes(3, 'big')
        return OxmTLV(oxm_field=self.oxm_field,
                      oxm_hasmask=oxm_hasmask,
                      oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        value = int.from_bytes(tlv.oxm_value[:3], 'big')
        if tlv.oxm_hasmask:
            pbb_isid_mask = int.from_bytes(tlv.oxm_value[3:], 'big')
            value = f'{value}/{pbb_isid_mask}'
        return cls(value)


class MatchEXTHDR(MatchField):
    """Match for IPV6 EXTHDR."""

    name = 'v6_hdr'
    oxm_field = OxmOfbMatchField.OFPXMT_OFB_IPV6_EXTHDR

    def as_of_tlv(self):
        """Return a pyof OXM TLV instance."""
        try:
            value = int(self.value)
            mask = None
            oxm_hasmask = False
        except ValueError:
            value, mask = map(int, self.value.split('/'))
            oxm_hasmask = True
        value_bytes = value.to_bytes(2, 'big')
        if mask:
            value_bytes += mask.to_bytes(2, 'big')
        return OxmTLV(oxm_field=self.oxm_field,
                      oxm_hasmask=oxm_hasmask,
                      oxm_value=value_bytes)

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return an instance from a pyof OXM TLV."""
        value = int.from_bytes(tlv.oxm_value[:2], 'big')
        if tlv.oxm_hasmask:
            exhead_mask = int.from_bytes(tlv.oxm_value[2:], 'big')
            value = f'{value}/{exhead_mask}'
        return cls(value)


class MatchFieldFactory(ABC):
    """Create the correct MatchField subclass instance.
    As OF 1.3 has many match fields and there are many ways to (un)pack their
    OxmTLV.oxm_value, this class does all the work of finding the correct
    MatchField class and instantiating the corresponding object.
    """

    __classes = {}

    @classmethod
    def from_name(cls, name, value):
        """Return the proper object from name and value."""
        field_class = cls._get_class(name)
        if field_class:
            return field_class(value)
        return None

    @classmethod
    def from_of_tlv(cls, tlv):
        """Return the proper object from a pyof OXM TLV."""
        field_class = cls._get_class(tlv.oxm_field)
        if field_class:
            return field_class.from_of_tlv(tlv)
        return None

    @classmethod
    def _get_class(cls, name_or_field):
        """Return the proper object from field name or OxmTLV.oxm_field."""
        if not cls.__classes:
            cls._index_classes()
        return cls.__classes.get(name_or_field)

    @classmethod
    def _index_classes(cls):
        for subclass in MatchField.__subclasses__():
            cls.__classes[subclass.name] = subclass
            cls.__classes[subclass.oxm_field] = subclass
