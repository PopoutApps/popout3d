project('popout3d',
  version: '1.6.44',
  meson_version: '>= 1.8.5'
)

bindir = get_option('bindir')
datadir = get_option('datadir')
pkgdatadir = join_paths(datadir, 'popout3d')

# -----------------------------
# Python executable
# -----------------------------
install_data('popout3d.py', rename: 'popout3d', install_dir: bindir)

# -----------------------------
# Data files
# -----------------------------
install_data('blank.png', install_dir: pkgdatadir)
#install_data('popout3d128x128.png', rename: 'com.github.PopoutApps.popout3d.png', install_dir: pkgdatadir)

# Icons
install_data('popout3d64x64.png', rename: 'com.github.PopoutApps.popout3d.png', install_dir: join_paths(datadir, 'icons', 'hicolor', '64x64', 'apps'))
install_data('popout3d128x128.png', rename: 'com.github.PopoutApps.popout3d.png', install_dir: join_paths(datadir, 'icons', 'hicolor', '128x128', 'apps'))

# -----------------------------
# Desktop & AppStream metadata
# -----------------------------
install_data('popout3d.desktop', install_dir: join_paths(datadir, 'applications'))
install_data('popout3d.metainfo.xml', install_dir: join_paths(datadir, 'metainfo'))

# -----------------------------
# Localisation
# -----------------------------
foreach lang : ['nl', 'de', 'es', 'fr']
  install_data('popout3d_' + lang + '.mo', rename: 'popout3d.mo',
               install_dir: join_paths(datadir, 'locale', lang, 'LC_MESSAGES'))
endforeach
