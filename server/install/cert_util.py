"""
Utilities related to SSL server/client certificates.
"""
import os
import logging
import threading
import binascii

from OpenSSL import crypto
#import cryptography as crypto


class CertAndKey(object):
    """
    Object that can optionally hold an OpenSSL X509 certificate and/or a keypair.
    Load Usage 1:
        cert = CertAndKey()
        cert.load_cert("bla.crt")
        cert.load_key("bla.key")
    Load Usage 2:
        cert = CertAndKey.load_from_files("bla.crt", "bla.key")
    Save Usage:
        cert.save_cert("bla.crt")    
        cert.save_key("bla.key")
        cert.save_pkcs12("bla.pfx")
    """
    def __init__(self, cert=None, key=None):
        self.cert = cert
        self.key = key
        
    def dump_cert(self, typ=crypto.FILETYPE_PEM):
        return crypto.dump_certificate(typ, self.cert)
        
    def save_cert(self, fname, typ=crypto.FILETYPE_PEM):
        with open(fname, "wb") as fp:
            fp.write(self.dump_cert(typ))
            
    def dump_key(self, passphrase=None, typ=crypto.FILETYPE_PEM):
        cipher = 'aes256' if passphrase else None
        return crypto.dump_privatekey(typ, self.key, cipher, passphrase)
        
    def save_key(self, fname, passphrase=None, typ=crypto.FILETYPE_PEM):
        with open(fname, "wb") as fp:
            fp.write(self.dump_key(passphrase, typ))
        
    def save_pkcs12(self, fname, passphrase):
        p12 = crypto.PKCS12()
        p12.set_certificate(self.cert)
        p12.set_privatekey(self.key)
        # TODO: what does p12.set_friendlyname() do?
        
        with open(fname, "wb") as fp:
            fp.write(p12.export(passphrase))
            
    def load_cert(self, cert_file, cert_type=crypto.FILETYPE_PEM):
        with open(cert_file, "rb") as fp:
            self.cert = crypto.load_certificate(cert_type, fp.read())        
            
    def load_key(self, key_file, passphrase=None, key_type=crypto.FILETYPE_PEM):
        with open(key_file, "rb") as fp:
            self.key = crypto.load_privatekey(key_type, fp.read(), passphrase)
        
    @classmethod
    def load_from_files(cls, cert_file, key_file, passphrase=None, cert_type=crypto.FILETYPE_PEM, key_type=crypto.FILETYPE_PEM):
        obj = cls(None, None)
        obj.load_cert(cert_file, cert_type)
        obj.load_key(key_file, passphrase, key_type)
        return obj
        

def generate_root_ca(out_cert_file=None, out_key_file=None, serial=1000, common_name="CA"):
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    # create a self-signed cert
    cert = crypto.X509()
    cert.set_version(2)
    cert.get_subject().C = "US"
    cert.get_subject().O = "Bla-%s" % os.urandom(4).hex() # Just so we never have multiple root CAs with the same subject.
    cert.get_subject().CN = common_name
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(-60*24*60*60) # 2 month ago
    cert.gmtime_adj_notAfter(10*365*24*60*60) # 10 years
    cert.set_pubkey(k)
    cert.set_issuer(cert.get_subject())    
    exts = [
        crypto.X509Extension(b"basicConstraints", True, b"CA:true"),
        crypto.X509Extension(b"keyUsage", True, b"digitalSignature,keyCertSign"),
        crypto.X509Extension(b"subjectKeyIdentifier", False, b"hash", subject=cert),
    ]
    cert.add_extensions(exts)
    cert.sign(k, 'sha256')

    res = CertAndKey(cert, k)
    if out_cert_file:
        res.save_cert(out_cert_file)
    if out_key_file:
        res.save_key(out_key_file)
    return res
         
def _generate_ssl_cert(ca_cert, dns_names=None, ip_addrs=None, common_name=None, serial=1000, 
                             out_cert_file=None, out_key_file=None, include_ca=False):
    assert isinstance(ca_cert, CertAndKey), "'ca_cert' must be a CertAndKey object"
    dns_names = list(dns_names) if dns_names else []
    ip_addrs = list(ip_addrs) if ip_addrs else []
    dns_list = ["DNS:%s" % dns for dns in dns_names]
    ip_list = ["IP:%s" % ip for ip in ip_addrs]
    san_str = str(",".join(dns_list + ip_list))
        
    
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    # Create the cert
    cert = crypto.X509()
    cert.set_version(2)
    cert.get_subject().C = "US"
    cert.get_subject().O = "Server"
    if common_name:
        cert.get_subject().CN = common_name
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(-30*24*60*60) # 1 month ago
    cert.gmtime_adj_notAfter(10*365*24*60*60) # 10 years
    cert.set_pubkey(k)
    cert.set_issuer(ca_cert.cert.get_subject())    
    exts = [
        crypto.X509Extension(b"basicConstraints", True, b"CA:false"),
        crypto.X509Extension(b"keyUsage", True, b"digitalSignature,keyEncipherment"),
        # TODO: Actually we don't need clientAuth unless this is a client SSL cert, in which case we don't need the serverAuth,
        # but who cares.
        crypto.X509Extension(b"extendedKeyUsage", False, b"serverAuth,clientAuth"),
        crypto.X509Extension(b"authorityKeyIdentifier", False, b"keyid", issuer=ca_cert.cert),
        crypto.X509Extension(b"subjectKeyIdentifier", False, b"hash", subject=cert),
    ]
    if san_str:
        exts.append(crypto.X509Extension(b"subjectAltName", False, san_str.encode()))
    cert.add_extensions(exts)    
    cert.sign(ca_cert.key, 'sha256')

    res = CertAndKey(cert, k)
    if out_cert_file:
        with open(out_cert_file, "wb")as fp:
            fp.write(res.dump_cert())
            if include_ca:
                fp.write(ca_cert.dump_cert())
    if out_key_file:
        res.save_key(out_key_file)
    return res                             
    
def generate_ssl_server_cert(ca_cert, dns_names=None, ip_addrs=None, common_name=None, serial=1000, 
                             out_cert_file=None, out_key_file=None, include_ca=False):
    """
    You must pass at least one DNS name or IP addr in 'dns_names'/'ip_addrs'. 'common_name' is
    used only for readability of the cert file, but is not used anymore for validation of the server during
    SSL session establishment.
    """
    if not dns_names and not ip_addrs:
        raise Exception("Cannot create a server SSL cert with no DNS/IP. 'common_name' is deprecated.")
    return _generate_ssl_cert(ca_cert, dns_names, ip_addrs, common_name, serial, out_cert_file, out_key_file, include_ca)
    
def generate_ssl_client_cert(ca_cert, dns_names=None, ip_addrs=None, common_name=None, serial=1000, 
                             out_cert_file=None, out_key_file=None):
    # No extra arg validation required.
    return _generate_ssl_cert(ca_cert, dns_names, ip_addrs, common_name, serial, out_cert_file, out_key_file)
    
def resign_cert(ca_cert, cert):
    assert isinstance(ca_cert, CertAndKey), "'ca_cert' must be a CertAndKey object"
    assert isinstance(cert, CertAndKey), "'cert' must be a CertAndKey object"
    cert.cert.set_issuer(ca_cert.cert.get_subject())
    cert.cert.sign(ca_cert.key, 'sha256')    
    
class SSLServerCertPool(object):
    """
    Cache of server SSL certificates that are dynamic created for different domains.
    This is used for SSL stripping servers.
    """
    # TODO: Support loading the certficates from the dir upon init, not just writing them.
    
    def __init__(self, base_dir_path, ca_cert):
        assert isinstance(ca_cert, CertAndKey), "'ca_cert' must be a CertAndKey object"
        self._dir_path = base_dir_path
        self._ca_cert = ca_cert
        self._cert_map = {}
        self._lock = threading.RLock()
        
    def get_cert_and_key_for_host(self, dns_names=None, ip_addrs=None, common_name="bla"):
        """
        common_name won't be used for the lookup, but only for generating the cert for the first time.
        This is because the usage of CN in certficates is deprecated. 
        """
        ip_addrs = ip_addrs or []
        dns_names = dns_names or []
        with self._lock:
            # It will look like: ("dns1", "dns2", "1.2.3.4", "1.2.3.5")
            name_list = tuple(sorted(list(dns_names) + list(ip_addrs)))
            cert_id = self._cert_map.get(name_list)
            need_generate = False
            if cert_id is None:
                need_generate = True
                cert_id = cert_id = os.urandom(4).encode("hex")
            else:
                logging.debug("Found SSL server cert (Id=%s) CN='%s', DNSs=%s, IPs=%s" % (
                                cert_id, common_name, str(dns_names), str(ip_addrs)))    
                
            cert_fname = os.path.join(self._dir_path, "%s.crt" % cert_id)
            key_fname = os.path.join(self._dir_path, "%s.key" % cert_id)
            
            if need_generate:
                # TODO: Maybe just take the unique 2nd degree TLDs and add wildcards?
                logging.info("Generating new SSL server cert (Id=%s) CN='%s', DNSs=%s, IPs=%s" % (
                                cert_id, common_name, str(dns_names), str(ip_addrs)))
                generate_ssl_server_cert(self._ca_cert, dns_names, ip_addrs, common_name=common_name,
                                        out_cert_file=cert_fname, out_key_file=key_fname, include_ca=True)
                self._cert_map[name_list] = cert_id
            
            return cert_fname, key_fname        
    
if __name__ == "__main__":
    ca = generate_root_ca("rootCA.crt", "rootCA.key", serial=0x12345, common_name="b2b-demo-CA")
    ca = CertAndKey.load_from_files("rootCA.crt", "rootCA.key")
    DNS_NAMES = ["localhost", "*.gigya.com", ]
    server = generate_ssl_server_cert(ca, DNS_NAMES, ["1.2.3.4", "1.2.3.5"], 
                                    common_name="b2b-demo-CA",
                                      out_cert_file="server3.crt", out_key_file="server3.key")