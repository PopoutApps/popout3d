project(
  'popout3d',
  version: '0.5.1',
  meson_version: '>= 0.46.0'
)

bindir = get_option('bindir')
datadir = get_option('datadir')
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), 'popout3d')

conf = configuration_data()
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'popout3d.in',
  output: 'popout3d',
  configuration: conf,
  install_dir: bindir
)

data_files = [
  'popout3d.glade',  
  'popout3d.png'
]

foreach file : data_files
  install_data(file, install_dir: pkgdatadir)
endforeach

install_data(
  'popout3d.desktop', rename : 'com.github.PopoutApps.popout3d.desktop'
  install_dir: join_paths(datadir, 'applications')
)
install_data(
  'popout3d.png', rename : 'com.github.PopoutApps.popout3d.png'
  install_dir: join_paths(datadir, 'icons', 'hicolor', '128x128', 'apps')
)
install_data(
  'popout3d64x64.png', rename : 'com.github.PopoutApps.popout3d.png'
  install_dir: join_paths(datadir, 'icons', 'hicolor', '64x64', 'apps')  
)
install_data(
	'popout3d_metainfo.xml', rename : 'com.github.PopoutApps.popout3d.appdata.xml'
  install_dir: join_paths(datadir, 'metainfo')  
)
