#include <string>
#include <vector>
#include <iostream>
#include <cassert>

#include <boost/foreach.hpp>
#include <boost/program_options.hpp>
namespace po = boost::program_options;

#include <TFile.h>
#include <TChain.h>
#include <TCut.h>


int main (int argc, char **argv)
{
  // define option flags
  po::options_description options("Options");
  options.add_options()
    ("help,h", "Show this help message")
    ("out,o", po::value<std::string>(), "Output ROOT file")
    ("cleaning-ver,c", po::value<unsigned>()->default_value(1),
     "Cleaning cut version (1, 2)")
    ("no-trigger,t", po::bool_switch()->default_value(false),
     "Do not apply trigger")
    ("factor,f", po::value<unsigned>()->default_value(120),
       "Reduction factor for event skimming")
    ;
  // define positional args
  po::options_description pos_args("Hidden options");
  pos_args.add_options()
    ("inputs", po::value<std::vector<std::string> >(),
     "ROOT files with TTree.  Name of the tree is assumed to be `DecayTree'.")
    ;
  // positional args
  po::positional_options_description pos;
  pos.add("inputs", -1);
  // combined options
  po::options_description all;
  all.add(options).add(pos_args);

  // parse arguments
  po::variables_map vm;
  try {
    // FIXME: they throw different exceptions, handle separately
    store(po::command_line_parser(argc, argv).
	  options(all).positional(pos).run(), vm); // po::required_option
    notify(vm);					   // po::error
  } catch (std::exception &e) {
    std::cout << e.what() << std::endl;
    return 2;
  }

  /* handle all options */
  std::string prog(argv[0]);
  auto usage = [prog, pos_args, options](){
    std::cout << "Usage: $ " << prog << " [options] " << "<files>\n" << std::endl;
    std::cout << "files - " << pos_args.find_nothrow("inputs", false)->description()
              << std::endl << std::endl;
    std::cout << options << std::endl;
  };
  // do nothing if help message requested
  if (vm.count("help")) {
    usage();
    return 0;
  }

  // enforce mandatory arguments
  if (not (vm.count("out") and vm.count("inputs")))
    {
      std::cout << "ERROR: Input or output file missing (both are mandatory).\n"
		<< std::endl;
      usage();
      return 1;
    }

  // cleaning cuts
  unsigned cleaning_v(vm["cleaning-ver"].as<unsigned>());
  TCut cut;
  // cleaning cut versions (apply in reverse order, w/o using break statements)
  switch (cleaning_v) {
    case 2:
      cut = cut && TCut("lab0_MM>5200");
    case 1:
      cut = cut && TCut("lab2_FDCHI2_ORIVX>=2");
      cut = cut && TCut("lab2_TAU>0");
    }

  // trigger
  bool notrigger(vm["no-trigger"].as<bool>());
  if (not notrigger) {
    TCut hlt1("lab0_Hlt1TrackAllL0Decision_TOS");
    TCut hlt2topo2body("lab0_Hlt2Topo2BodyBBDTDecision_TOS");
    TCut hlt2topo3body("lab0_Hlt2Topo3BodyBBDTDecision_TOS");
    TCut hlt2topo4body("lab0_Hlt2Topo4BodyBBDTDecision_TOS");
    TCut hlt2incphi("lab0_Hlt2IncPhiDecision_TOS");
    TCut hlt2 = hlt2topo2body || hlt2topo3body || hlt2topo4body || hlt2incphi;
    cut = cut && hlt1 && hlt2;
  }

  // input files
  std::vector<std::string> filenames(vm["inputs"].as<std::vector<std::string> >());
  // add files to chain
  TChain itree("DecayTree");	// assumes tree inside files are named "DecayTree"
  BOOST_FOREACH(std::string filename, filenames) {
    itree.AddFile(filename.c_str());
  }
  unsigned long nentries(itree.GetEntries());

  // skimming factor
  unsigned factor(vm["factor"].as<unsigned>());

  // output file
  std::string ofilen(vm["out"].as<std::string>());
  TFile *ofile = TFile::Open(ofilen.c_str(), "recreate");
  // For one of MU/MD, data: 67798586L, MC (Dsπ): 67837L
  std::cout << "Selection: " << cut << std::endl;
  std::cout << "Entries: " << (nentries/factor) <<   std::endl;
  TTree *otree = itree.CopyTree(cut, "", nentries/factor);
  otree->Write();
  ofile->Write();
  ofile->Close();
  return 0;
}
