# Maintainer: Samy Abdellatif
# Contributor: Samy Abdellatif
pkgname=netui-gtk
pkgver=1.0.0
pkgrel=1
pkgdesc="A lightweight GTK+ utility to manage network interfaces, routes, and DHCP"
arch=('any')
url="https://github.com/samyabdellatif/netui-gtk"
license=('MIT')
depends=('python' 'python-gobject' 'gtk3' 'iproute2')
optdepends=(
    'dhcpcd: DHCP client support'
    'dhclient: ISC DHCP client support'
    'networkmanager: NetworkManager integration'
    'systemd: systemd-networkd integration'
    'wpa_supplicant: Wi-Fi authentication support'
    'netctl: Arch Linux network profile manager'
)
install="$pkgname.install"
source=("$pkgname-$pkgver.tar.gz" "$pkgname.install")
sha256sums=('40fe59db1c568b948a885ce641fde413c1ac5d73050b182d9bf8ce9b8a1adf5d' '5b139aceb66ee8373974125779633a06301cb3af5ed776a4bd0f4375763cfc02')

package() {
    # Create directory structure
    install -d "$pkgdir/usr/share/$pkgname"
    install -d "$pkgdir/usr/share/$pkgname/styles"
    install -d "$pkgdir/usr/share/$pkgname/netmanage"
    install -d "$pkgdir/usr/bin"
    install -d "$pkgdir/usr/share/applications"
    install -d "$pkgdir/usr/share/pixmaps"
    install -d "$pkgdir/usr/share/polkit-1/actions"

    # Copy application files
    install -m 644 __main__.py "$pkgdir/usr/share/$pkgname/"
    install -m 644 __init__.py "$pkgdir/usr/share/$pkgname/"
    install -m 644 netui.py "$pkgdir/usr/share/$pkgname/"
    install -m 644 config.py "$pkgdir/usr/share/$pkgname/"
    install -m 644 manual_config.py "$pkgdir/usr/share/$pkgname/"
    install -m 644 advanced_config.py "$pkgdir/usr/share/$pkgname/"
    install -m 644 check_system.py "$pkgdir/usr/share/$pkgname/"
    install -m 644 styles/style.css "$pkgdir/usr/share/$pkgname/styles/"
    install -m 644 netmanage/*.py "$pkgdir/usr/share/$pkgname/netmanage/"

    # Copy icon
    install -m 644 netui.ico "$pkgdir/usr/share/$pkgname/"
    install -m 644 netui.ico "$pkgdir/usr/share/pixmaps/$pkgname.ico"

    # Copy desktop file
    install -m 644 "$pkgname.desktop" "$pkgdir/usr/share/applications/"

    # Copy polkit policy
    install -m 644 com.github.netui-gtk.policy "$pkgdir/usr/share/polkit-1/actions/"

    # Create launcher script
    cat > "$pkgdir/usr/bin/$pkgname" << EOF
#!/bin/sh
exec python3 /usr/share/$pkgname/__main__.py "\$@"
EOF
    chmod 755 "$pkgdir/usr/bin/$pkgname"
}