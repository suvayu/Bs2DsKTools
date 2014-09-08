#include <string>
#include <vector>
#include <iostream>
#include <cassert>
#include <limits>

#include <boost/foreach.hpp>
#include <boost/program_options.hpp>
namespace po = boost::program_options;

#include <TFile.h>
#include <TTree.h>


int main (int argc, char **argv)
{
  // define option flags
  po::options_description options("Options");
  options.add_options()
    ("help,h", "Show this help message")
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
  if (not vm.count("inputs"))
    {
      std::cout << "ERROR: Input file missing (mandatory).\n" << std::endl;
      usage();
      return 1;
    }

  // input files
  std::vector<std::string> filenames(vm["inputs"].as<std::vector<std::string> >());
  BOOST_FOREACH(std::string filename, filenames) {
    std::cout << "Updating file: " << filename << std::endl;
    TFile ifile(filename.c_str(), "update");
    TTree *itree = dynamic_cast<TTree*>(ifile.Get("DecayTree"));
    assert(itree);

    unsigned long nentries(itree->GetEntries());
    std::cout << "Entries: " << nentries << std::endl;

    double lab1_gp,
      lab3_gp, lab3_pt, lab3_chi2,
      lab4_gp, lab4_pt, lab4_chi2,
      lab5_gp, lab5_pt, lab5_chi2;

    itree->SetBranchAddress("lab1_TRACK_GhostProb", &lab1_gp);
    itree->SetBranchAddress("lab3_TRACK_GhostProb", &lab3_gp);
    itree->SetBranchAddress("lab4_TRACK_GhostProb", &lab4_gp);
    itree->SetBranchAddress("lab5_TRACK_GhostProb", &lab5_gp);

    itree->SetBranchAddress("lab3_PT", &lab3_pt);
    itree->SetBranchAddress("lab4_PT", &lab4_pt);
    itree->SetBranchAddress("lab5_PT", &lab5_pt);

    itree->SetBranchAddress("lab3_IPCHI2_OWNPV", &lab3_chi2);
    itree->SetBranchAddress("lab4_IPCHI2_OWNPV", &lab4_chi2);
    itree->SetBranchAddress("lab5_IPCHI2_OWNPV", &lab5_chi2);

    std::vector<double> ghost_prob, trk_pt, trk_chi2;
    std::vector<double> *pghost_prob(&ghost_prob), *ptrk_pt(&trk_pt), *ptrk_chi2(&trk_chi2);
    ghost_prob.reserve(4);
    trk_pt.reserve(3);
    trk_chi2.reserve(3);

    itree->Branch("ghost_prob", "std::vector<double>", &pghost_prob);
    itree->Branch("trk_pt", "std::vector<double>", &ptrk_pt);
    itree->Branch("trk_chi2", "std::vector<double>", &ptrk_chi2);

    int bytes(0);
    for(unsigned i = 0; i < nentries; ++i) {
      bytes += itree->GetEntry(i);
      if (i%10000 == 0) std::cout << "@entry: " << i
				  << ", bytes read so far: " << bytes << std::endl;
      assert(lab1_gp > 10*std::numeric_limits<double>::epsilon()
	     or lab1_gp <= 0);

      ghost_prob.push_back(lab1_gp);
      ghost_prob.push_back(lab3_gp);
      ghost_prob.push_back(lab4_gp);
      ghost_prob.push_back(lab5_gp);

      trk_pt.push_back(lab3_pt);
      trk_pt.push_back(lab4_pt);
      trk_pt.push_back(lab5_pt);

      trk_chi2.push_back(lab3_chi2);
      trk_chi2.push_back(lab4_chi2);
      trk_chi2.push_back(lab5_chi2);

      itree->Fill();

      // cleanup
      ghost_prob.clear();
      trk_pt.clear();
      trk_chi2.clear();
    }

    // cleanup
    itree->Write(); delete itree; ifile.Close();
  }
  return 0;
}
