import os
import pytest
import sslcrypto
import sslcrypto.fallback


def _test(curve):
    priv1 = curve.new_private_key()
    pub1 = curve.private_to_public(priv1)
    priv2 = curve.new_private_key()
    pub2 = curve.private_to_public(priv2)
    priv3 = curve.new_private_key()
    pub3 = curve.private_to_public(priv3)
    data = b"Hello, world!"
    data2 = b"Just a test"

    # ECDH
    assert curve.derive(priv1, pub2) == curve.derive(priv2, pub1)
    assert curve.derive(priv1, pub2) != curve.derive(priv3, pub1)

    # ECIES
    assert curve.decrypt(curve.encrypt(data, pub1), priv1) == data
    with pytest.raises(ValueError):
        if curve.decrypt(curve.encrypt(data, pub1), priv2) != data:
            # We have to handle this case separately because AES might
            # accidentally manage to decrypt data with a wrong key
            raise ValueError("Got wrong data")

    # ECDSA
    assert curve.recover(curve.sign(data, priv1, recoverable=True), data) == pub1
    assert curve.verify(curve.sign(data, priv1), data, pub1)
    assert curve.verify(curve.sign(data, priv1, recoverable=True), data, pub1)
    # Unrecoverable signature
    with pytest.raises(ValueError):
        curve.recover(curve.sign(data, priv1), data)
    # Wrong data
    curve.recover(curve.sign(data, priv1, recoverable=True), data2) != pub1
    # Wrong public key
    with pytest.raises(ValueError):
        curve.verify(curve.sign(data, priv1), data, pub2)
    # Wrong data
    with pytest.raises(ValueError):
        curve.verify(curve.sign(data, priv1), data2, pub1)


# Show different curves as different testcases
for name in sslcrypto.ecc.CURVES:
    def _gen(name):  # Closure
        # Pure-Python implementation
        curve = sslcrypto.fallback.ecc.get_curve(name)
        globals()["test_{}".format(name)] = lambda: _test(curve)

        # Try testing native version as well
        if sslcrypto.ecc is not sslcrypto.fallback.ecc:
            native_curve = sslcrypto.ecc.get_curve(name)
            globals()["test_native_{}".format(name)] = lambda: _test(native_curve)

    _gen(name)