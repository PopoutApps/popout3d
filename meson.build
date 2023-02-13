project(
  'popout3d',
  version: '1.6.01',
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

data_files = [
  'popout3d.png',                       #for Glade ??? for About???
  'com.github.PopoutApps.popout3d.png', #maybe desktop icon
  'dummy.png'
]

foreach file : data_files
  install_data(file, install_dir: pkgdatadir)
endforeach

install_data(
  'com.github.PopoutApps.popout3d.desktop',
  install_dir: join_paths(datadir, 'applications')
)

install_data(
  'popout3d.png', rename : 'com.github.PopoutApps.popout3d.png',
  install_dir: join_paths(datadir, 'icons', 'hicolor', '128x128', 'apps')
)

install_data(
  'com.github.PopoutApps.popout3d.png',
  install_dir: join_paths(datadir, 'icons', 'hicolor', '64x64', 'apps')  
)

install_data(
  'com.github.PopoutApps.popout3d.appdata.xml',
  install_dir: join_paths(datadir, 'metainfo')  
)
