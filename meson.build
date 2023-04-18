project(
  'popout3d',
  version: '1.6.04',
  meson_version: '>= 0.46.0'
)

bindir = get_option('bindir')
datadir = get_option('datadir')
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), 'popout3d')

conf = configuration_data()
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'popout3d.py',
  output: 'popout3d',
  configuration: conf,
  install_dir: bindir
)

# dummy image and logo for About
data_files = [
  'com.github.PopoutApps.popout3d.png',
  'dummy.png'
]

foreach file : data_files
  install_data(file, install_dir: pkgdatadir)
endforeach

# per requirements
install_data(
  'com.github.PopoutApps.popout3d.appdata.xml',
  install_dir: join_paths(datadir, 'metainfo')  
)

install_data(
  'com.github.PopoutApps.popout3d.desktop',
  install_dir: join_paths(datadir, 'applications')
)

install_data(
  'com.github.PopoutApps.popout3d.png',
  install_dir: join_paths(datadir, 'icons', 'hicolor', '128x128', 'apps')  
)

install_data(
  'com.github.PopoutApps.popout3d64x64.png', rename : 'com.github.PopoutApps.popout3d.png',
  install_dir: join_paths(datadir, 'icons', 'hicolor', '64x64', 'apps')
)

# language files
install_data(
  'popout3d_nl_NL.mo', rename : 'popout3d.mo',
  install_dir: join_paths(get_option('prefix'), get_option('localedir'), 'nl_NL', 'LC_MESSAGES')
)

install_data(
  'popout3d_de_DE.mo', rename : 'popout3d.mo',
  install_dir: join_paths(get_option('prefix'), get_option('localedir'), 'de_DE', 'LC_MESSAGES')
)
